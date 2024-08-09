import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException
import time
from collections import Counter
import logging

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['api']['delay_time'])
N_MINIMUM = int(config['rs']['n_minimum_playlist_songs'])
N_SCRAPE = int(config['rs']['n_scrape'])

# Spotify API credentials
client_credentials_manager = SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()


def load_existing_ids():
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


existing_songs, existing_artists, existing_playlists = load_existing_ids()


def fetch_playlist_tracks(playlist_id):
    logger.info(f'Fetching tracks from playlist {
                playlist_id} with a limit of {N_SCRAPE} items')
    track_ids = []
    limit = N_SCRAPE

    try:
        results = sp.playlist_tracks(playlist_id)
        while results and len(track_ids) < limit:
            for item in results['items']:
                track = item.get('track')
                if track:
                    track_id = track.get('id')
                    if track_id:
                        track_ids.append(track_id)
                else:
                    logger.warning(f'Unexpected track item structure: {item}')
            if len(track_ids) >= limit or not results['next']:
                break
            results = sp.next(results)
            time.sleep(DELAY_TIME)
    except SpotifyException as e:
        logger.error(f"Error fetching playlist tracks: {e}")

    return track_ids[:limit]


def fetch_track_details_and_audio_features(track_ids):
    logger.info(f'Fetching track details and audio features for multiple tracks')
    track_data = []
    try:
        tracks = sp.tracks(track_ids)['tracks']
        audio_features = sp.audio_features(track_ids)

        # Ensure both tracks and features are the same length
        if len(tracks) != len(audio_features):
            logger.warning(
                "Mismatch between number of tracks and audio features")

        for track, features in zip(tracks, audio_features):
            if track and features:
                try:
                    track_data.append((
                        track['id'], track['name'],
                        [artist['id'] for artist in track['artists']],
                        features['acousticness'], features['danceability'],
                        features['energy'], features['instrumentalness'],
                        features['key'], features['liveness'],
                        features['loudness'], features['mode'],
                        features['speechiness'], features['tempo'],
                        features['time_signature'], features['valence']
                    ))
                except KeyError as e:
                    logger.warning(
                        f"Missing expected feature in track or audio features: {e}")
            else:
                if not track:
                    logger.warning(f"Missing track details for some tracks")
                if not features:
                    logger.warning(f"Missing audio features for some tracks")

    except SpotifyException as e:
        logger.error(f"Error fetching track details and audio features: {e}")

    return track_data


def fetch_artist_details(artist_ids):
    logger.info(f'Fetching artist details for multiple artists')
    artist_data = []
    try:
        artists = sp.artists(artist_ids)['artists']
        for artist in artists:
            if artist:
                artist_data.append((
                    artist['id'], artist['name'], ','.join(artist['genres'])
                ))
    except SpotifyException as e:
        logger.error(f"Error fetching artist details: {e}")

    return artist_data


def record_exists(table_name, record_id):
    cursor.execute(f'SELECT 1 FROM {table_name} WHERE {
                   table_name[:-1]}_id = ?', (record_id,))
    return cursor.fetchone() is not None


def update_playlist_metrics(playlist_id, track_ids):
    logger.info(f'Updating metrics for playlist {playlist_id}')
    if not track_ids:
        return

    track_details = []
    for track_id in track_ids:
        cursor.execute('SELECT * FROM songs WHERE song_id = ?', (track_id,))
        track_details.append(cursor.fetchone())

    artist_counts = Counter()
    genre_counts = Counter()
    audio_features = {feature: [] for feature in [
        'acousticness', 'danceability', 'energy', 'instrumentalness',
        'key', 'liveness', 'loudness', 'mode', 'speechiness',
        'tempo', 'time_signature', 'valence']}

    track_genres = []

    for details in track_details:
        if details:
            _, _, artist_ids, *features = details
            artist_ids = artist_ids.split(',')
            for artist_id in artist_ids:
                cursor.execute(
                    'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
                artist_genres = cursor.fetchone()
                if artist_genres:
                    genres = artist_genres[0].split(',')
                    track_genres.extend(genres)
                    genre_counts.update(genres)
                artist_counts[artist_id] += 1
            for feature, value in zip(audio_features.keys(), features):
                audio_features[feature].append(value)

    most_common_genres = set(genre for genre, _ in genre_counts.most_common(1))

    minority_track_ids = set()
    for details in track_details:
        if details:
            _, _, artist_ids, *features = details
            artist_ids = artist_ids.split(',')
            for artist_id in artist_ids:
                cursor.execute(
                    'SELECT artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
                artist_genres = cursor.fetchone()
                if artist_genres:
                    genres = set(artist_genres[0].split(','))
                    if not genres & most_common_genres:
                        minority_track_ids.add(details[0])

    filtered_track_ids = [
        track_id for track_id in track_ids if track_id not in minority_track_ids]

    top_artists = [artist_id for artist_id, _ in artist_counts.most_common(20)]
    top_genres = [genre for genre, _ in genre_counts.most_common(20)]

    top_artists += [None] * (20 - len(top_artists))
    top_genres += [None] * (20 - len(top_genres))

    min_max_features = {feature: (min(values), max(values)) if values else (None, None)
                        for feature, values in audio_features.items()}

    cursor.execute('''
        UPDATE playlists SET 
            playlist_top_artist_ids = ?, 
            playlist_top_genres = ?, 
            min_acousticness = ?, max_acousticness = ?, 
            min_danceability = ?, max_danceability = ?, 
            min_energy = ?, max_energy = ?, 
            min_instrumentalness = ?, max_instrumentalness = ?, 
            min_key = ?, max_key = ?, 
            min_liveness = ?, max_liveness = ?, 
            min_loudness = ?, max_loudness = ?, 
            min_mode = ?, max_mode = ?, 
            min_speechiness = ?, max_speechiness = ?, 
            min_tempo = ?, max_tempo = ?, 
            min_time_signature = ?, max_time_signature = ?, 
            min_valence = ?, max_valence = ?,
            playlist_items = ?
        WHERE playlist_id = ?
    ''', (
        ','.join(filter(None, top_artists)), ','.join(
            filter(None, top_genres)),
        *[min_max_features[feature][i] for feature in [
            'acousticness', 'danceability', 'energy', 'instrumentalness',
            'key', 'liveness', 'loudness', 'mode', 'speechiness',
            'tempo', 'time_signature', 'valence'] for i in range(2)],
        ','.join(filtered_track_ids),
        playlist_id
    ))
    conn.commit()


def process_playlist(playlist_id):
    logger.info(f'Processing playlist {playlist_id}')
    try:
        if playlist_id in existing_playlists:
            logger.info(f"Playlist with ID: {playlist_id} already exists.")
            return

        playlist_details = sp.playlist(playlist_id)
        total_tracks = playlist_details['tracks']['total']

        if total_tracks >= N_MINIMUM:
            track_ids = fetch_playlist_tracks(playlist_id)
            new_song_ids = set()
            valid_track_ids = []

            track_ids_to_fetch = [
                track_id for track_id in track_ids if track_id not in existing_songs]
            track_details = fetch_track_details_and_audio_features(
                track_ids_to_fetch)

            for track_detail in track_details:
                if track_detail:
                    song_id, song_name, artist_ids, *track_features = track_detail
                    cursor.execute('''
                        INSERT OR REPLACE INTO songs (
                            song_id, song_name, artist_ids, acousticness, 
                            danceability, energy, instrumentalness, 
                            key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (song_id, song_name, ','.join(artist_ids), *track_features))

                    new_song_ids.add(song_id)
                    valid_track_ids.append(song_id)

                    artist_ids_to_fetch = [
                        artist_id for artist_id in artist_ids if artist_id not in existing_artists]
                    artist_details = fetch_artist_details(artist_ids_to_fetch)

                    for artist_detail in artist_details:
                        if artist_detail:
                            cursor.execute('''
                                INSERT OR REPLACE INTO artists (
                                    artist_id, artist_name, artist_genres
                                ) VALUES (?, ?, ?)
                            ''', artist_detail)
                else:
                    logger.warning(
                        "Failed to fetch details for track ID: {track_id}")
            valid_track_ids += [
                track_id for track_id in track_ids if track_id not in new_song_ids]

            track_ids_str = ','.join(valid_track_ids)
            cursor.execute('''
                INSERT OR REPLACE INTO playlists (
                    playlist_id, playlist_creator_id, playlist_original_items, 
                    playlist_items_fetched, playlist_items
                ) VALUES (?, ?, ?, ?, ?)
            ''', (playlist_id, playlist_details['owner']['id'], total_tracks, len(valid_track_ids), track_ids_str))

            conn.commit()

            update_playlist_metrics(playlist_id, valid_track_ids)
        else:
            logger.info(f"Skipping playlist with ID: {
                        playlist_id} because it has fewer than {N_MINIMUM} tracks.")
    except SpotifyException as e:
        logger.error(f"Error processing playlist with ID: {playlist_id}: {e}")


def fetch_user_playlists(username):
    logger.info(f'USER: https://open.spotify.com/user/{username}')
    playlists = []
    try:
        results = sp.user_playlists(username)
        while results:
            playlists.extend(
                item['id'] for item in results['items'] if not item['collaborative'] and item['public']
            )
            if not results['next']:
                break
            results = sp.next(results)
            time.sleep(DELAY_TIME)
    except SpotifyException as e:
        logger.error(f"Error fetching playlists for user {username}: {e}")
    return playlists


usernames = ["31hja4lsru3ub6nwjvrxmabkk6pe", "31d7u5fzqvorcky7ta2a67ivvywa", "50tidsvdg5vzvlx477zu77k8z", "31n7wtvilvpby2gdw3erhcjd2hvq", "31wm4wommdlkpxkzk6t244wtbilq", "31rqmtepujqlp3a2v27f6wcyur4q", "31l5rqzc6irxfnlb54rkhijmunhu", "b63xf6ta9jmubqti6u69w2vxk", "316idi7jng5e6qkhw3h4pvabddke", "t1looi81ehdm5pv4cf51w8lzc", "31apgqa2iq3vn5qqh74bokcjcgje", "31zwuktk4hv4pv3bpoigypbyzkkm", "2nrcpuuoqtr9chd8oqjod2n0x", "315g2qcvo4lu534gaz6uy5tduy6e", "pzits36wic4w25tllrm0wbafd", "qcrlh1oc77h7lhhk7qxvwk1j1", "31eserlzmp4qtydfvgnyzebuk3oq", "312sl2yo5c3gvbsfqjuxsrba7cya", "ihx97gl9mpsj3wmmx5os2dkoc", "n4mbh3s243gjb5dwenngdmmr9", "31m4qmj3bthhlslxlh7bmvnyyoqq", "zgbmk1w9yc2v95hx3ypnjjo7s", "o6mz1tnnsnmlsvp944ulrfeba", "31symu2nioxazgyxyoabccna4x7i", "31czulme2q6fkh7pavw656kae3dy", "55p2pkj2zl2ivckxhmjoa4y2x", "67mmxu4j95ggjky4xbxd5w7bt", "zxg2863l3n8i6b9sm007rni9n", "312mpl6yiz7fmag4ghsmkur2phqq", "31k66jpp6ylfmkawntbvit6ijqzq", "31zui2ffdfc5z5ztx4exloumdz3y", "31h5i2dsuxq5q4uqf3kpyzkxrkde", "4ueru446vwbv0xpootfd0abda", "yhh0yk1jhrnl89amf90d3hsi4", "31a2xawrxasntlorbbvvk7xloqcy", "31h6bueagtsnjerjkqpykos7ltvq", "316hdnevcq4h7gzhntymg73gafyu", "31qvg3nx4ykrgjje3cvl4rimcilm", "31tonjdvca6azarejylugeoufmxm", "31pqpmte7r7nqhe55kjjbhw7z3de", "317kxsy3xbdasfeljv7li56io76e", "31b7ybx5d4aadloxdkcmmezrbhye", "31mhcvkz736fbxqsfytc4v2tb5mu", "31tymexy553dkxell4tp6v6alw4q", "plpd012c5fxhmqj8h83ybbv99", "31gb4dzcp75qhwuleizbsyw5rp7e", "31zrjrrggjwjkskh6adqioshxegy", "31s3txv4plyfgoz6kavmbtn2po4y", "ch23205ctn4hnudavam94uzna", "31pp6i5wxctzagljza7reb2mits4", "2k6r9ho9prz56zzhmde96wmf0", "31s25xgb3b3wm3scx7hht3zkfdui", "31jofxeqgawxrzg5l6uhiws7p2h4", "3146oo3tla3ogoro5cvsxipodg24", "316itp2hq4gj5colb63ktzcbpdui", "b34xs5iqoiio0oehvf8t5kfci", "31mibgus5qifdvdymscnz4wiee6q", "31wf62vmo4vgdzplrmrysilrryi4", "31ib57srpcedciqzi2mky4k473le", "31rl2im2lkjydgsj6jewqvc6pxse", "31tmd5opqyktdjo3nvupgulp3scm", "n2snrl8t69ipr40shqscy001e", "qj7ce9lfgwd43g4v3217wrye2", "31q7p25toeqjvdkszo6uugfaxfvm", "31iodj7p7exghp2pi6sesf3ycuki", "jvwvvveid1mszsk71gq2rgxrp", "312d3prmgko35bauxiqrcg5kkwdu", "31g5bt5v3dl4nezavcicjmwhu3cy", "31mj2nwdesfkumcfrvykxeidow3a", "y8udae3ii17sahcngvstyril7", "jowd94eoogxe667rl13j4q2tt", "31xno24p63mhabam47p43gsjrd3y", "316nfbrjqfyvawasqpua2g7wgoae", "1218946967", "ms3youp3tehyq0h8uctvkj1di", "31oxgb36mctnkikkk677dwpqpqza", "rk2h1bi8yuhkg0n6proaobqkb", "31xvb5dwguujxeuld2nbyr6cq3cu", "31cd2wp3oe5fjaqllcssspfqy5zu", "31lga2xatuysehljwkmoy7iabnoa", "31my2lugvuqhadteiniptmg3tu5q", "31frmuhcgvbogsen2w2kgafgfvse", "31mt3xhu6pahb4qs2odsboqgliwy", "31b4giqqpm3dfxftao3fgenekmem", "31ihy72rlvhrpagdrowncty3bq5u", "31r42sbvg3d5sr2k6wea3wtmvoty", "v7clemox03dkw7l80dbnnyx4i", "31f76kg2deogztzavj3s4hseuhzy", "31d2wv6nbivzasqd4yhnpich654y", "31ejxc3zdgor32arkn6bnmiv5vhu", "31pvayu7viirqdwqnvojbvhodapu", "316uadraywmipsjft6tzmcpmwuhe", "5buk2jo751xsbo6m4lfpffa79", "31pstm2iuaor7op5gtzhepdrseam", "p29vyr65alnsz5oa3bglkerlt", "31cnobohhvz4a6gi25e2ivcmqoxm", "16hpkdqpao5uwrpetb160f3bv", "6ztjnj38kd96ymws2l72tcvf2", "c8t3r4b9qpa5gabd26gfashpa", "02l516u6cz4qni0vqehtegmbx", "jillsyaa", "35y054uuahljb7zxfxnani31o", "3167dwpdbsizq6yvinovz4d5rt5e", "dgorwinx9e463b55li66siubw", "31jn6qkxggjowakkjnymc336yrmi", "3147xhyrmj6utnsn4aqrjv4qjsle", "31craqpzgivm2utrch533kbqpt5m", "312i4rvya5e4j4qnrwwbfzgqjwba", "4mraq2xb0jbz7b0trfgzpvh8m", "yc1xcy4mi66idnho1ot74b1wo", "31f2kaonuqawi5jf3hlr72pqq43m", "9u2v4wc4nxyrfnn7g1uzb3z7x", "31ge3mcnekl5t2cjfin7yhotjinm", "31o55ehehysrqrbprvj5uxihvjfa", "31zr7p3aeb6o2f62bn7c57r7juma", "5nr8m2xx11n3v0djdwpuyhmvg", "31ikhcrdz4qsk22dp2kvofavwqna", "bfbii4f324u11vjvow4nhfjtu", "31axtqo46lwc5s5gjvukiesgs4la", "31ye6qli2rdghsvzvk7ebxwzrqpe", "ai9ns4qctbuxqfuw9tyqwjy2u", "31b76sggmw64m2yjl2nuoee67a6i", "getmusicindonesia", "obg55uhsjatc796sxtrcc3o16", "6y5bthnbcsfqpdu5xeu9gtey9", "31q5tdu3kxj3lqri3e7mekrirs7m", "31afyz2taj2ov6k5g2eb7qjrzyve", "315zaxoblj6ef4sbwgdfsw2p3zya", "el5ce55t0selupbqs0kvqsljo", "sausanbawazir", "31oxwxzfubwtz6kccd35z4bodxeu", "31tqmmrwwycch4xi4nwesror7xzi", "31yduyunp5o46a5ys3qkq2tdmv5q", "31mr5n2kctqgtsbyuuf2pxgn2fwe", "31echrpvcemdvmdcshgudrhx5vm4", "31i4yxjgkab3t6rvnj4jbvyw5uvq", "31skrj2qtvplnjfc54qycag72cia", "31i44joqoctd76p6yp253jmxx76i", "sl56s1wmz5k8m29vzfjy47qja", "31eqtlgnt75gld6iljn7qgs76ce4", "31la6ysubzliwssxzhvqjh7kjiji", "31hwpfhtjfzfcwyp7hjj3xb254iu", "313khwop3rg4jpilvoqn7ygssh6i", "31vrmv6nwlgkpcv5o7vleesvfchi", "3487jh95m2pix2f5vk7pgebzy", "31h4lys3fgad2kbnnswrauvmn5nq", "31bcpfhqgtddyjywyr4uczj6yb2m", "314xkddifx3q7etk6vdgynskw2fu", "yt9wssq8go83mvplh245qopeo", "31iddudpyapmpgttadfimg5uudqi", "31qob5meb2gfyln2y5kdijmtefby", "9ynjum2lz73skao2yiq21lkft", "31jqvvqonuomjbubncgbijsuvkmq", "wcbsaihahde92pg0pnya7mfkl", "31wqo3qphdmqjsjhmmsr4hkrce5m", "31ww7inn5r5euwimfrczosr32bxa", "acx25wofd8xn0742vv5wz8dln", "31cdnbvmayd4pgxkpeob7r5h3d5a", "ci8l4si5fzezjk0i72hzlfvj9", "314w57shfbtlaco4a6aq3zlq6ln4", "gz2azo3nlkc8kysbxa90engvz", "316qw75ad4o5tp5g2o6zdjfy3gxa", "i2chdc8e0tv0eg3qf6gmc2wuw", "31fuaorpj6drjtcqvltmw3qb5i44", "31jbatpo7pwzsrznywy3gtjtayoa", "wgtfbj2qzg3our00jgnwi9gw3", "31ckwv3lw5jlvu3ktkqrsv6gaid4", "kjbeconws95t73tkyvak516fd", "shbrnavega", "314muxdjzfh5sv2a4rhfwlr3scjq", "315tsgtgwvbekwjwahbbc5bzrlxm", "31sixv5twzjmbrybqvqtudye7hce", "31oy6ht5srwwr3clotht3vio37za", "31s3qyswd24ka7ug4cw5bajlvyrm", "31o74ygtfg5nk7rjwornzbjf2pa4", "31wfrxemnmcwofzeyfev2zexra5q", "31gucjjnaeuph5y74bu42rzwp4j4", "31osjk4uuk2b6i7ty6imgcquzegq", "5s9u48xridz8gkkwwmvrkdo3c", "31qwyngfhbofeumzvycpmmq7g3ne", "31afo4gmetqc7xu4mo4dr67yrwwe", "31y2xw5ptphcrejoronno3yfwsqe", "31oc55yehhrgkmhartfntgutomwi", "tppdwj0cs99w4s9kn7022mk0y", "31s4udlben2ssbbtiqclxfqgq4dm", "mkhctfd8k523xvq2l4eizk8sm", "rm3095whkjr0ho0jv27uav4go", "31avjtd3e2fvevow7hapvdhif3c4", "31hwqgjg7otwofctr3cvqzk7o63q", "vf33u4p2fcoqxyoh1frgk4b38", "31amca6vjtafuxzvajp2hedutdbm", "31n7wfakspbxngazhshrqzojtvyu", "31vvnv6eue6h5mqegbn3gleri4ne", "31bym3mguccsq5m3ftnren7dpdgm", "31oi76l6doossyi72anqo45dquoy", "31fmsouttquimm47rsqu6muznlui", "31kc65cpg5svxk744fryogvx6fba", "6om38x4dpb9mgfip5hdrug7kn", "70e0014i29n8tydbewjq3strb", "32otv0abuehsb702qytd7weij", "31gpn4hyghgppcseel4miw7bkevy", "31i3qxauigud5x5ft7vvdckfvv2a", "31eu7u5lqrdirx3snt3asqenea7e", "31tzunld4wpb3iqfvoha6t5pz4mm", "f30n7fgy28vq1msg2v15r1159", "riskyfadly", "r9pbhp3slzrqxd9cajfu4otxl", "31uwmqmydmuzrmi2z55vb43rm6tu", "p4so735x25w2rm967psjjrdcq", "31jqexn4gqb2t3vl5e7s2j45hlc4", "31rac5wprq73yc7qbn42e64frgy4", "wg5fyqhd332mbfdbjhnqgf7rq", "kmhedmmidzwa0z6iwvietfy6e", "wfamx7a493k4uqakselt2dxre", "31oibq3eip6mzbyxsvkahednyhsm", "31nha23rnp5vja4qidpkxi2ne3qe", "31ef4acvrdmg2atr2usl6dwtcfq4", "thesoundsofspotify", "31rlfn3mwzf6nq7rxs4nymyubzda", "kuqrwhkrov0jctkvr4ntzktke", "qes68r0knjx1twhjn43it74d6", "qkhwh2zeux67q6gyc99rmiqzs", "dandidaro", "31l5txw6x7y3f6jmoxkxzfnux2py", "31hjkaefp5eoqnnjibegw2r5nfui", "31src3noax7l4w4uks6iekpn3csu", "31ytcsf3t7nlspzu4ti2pmdbtq4i", "31idcvk3sf2qsjtpx6mbrlv6gsoq", "315zz77phwrc252t7g4s2vdzmlrm", "489bz9nhphll8qd94ksih2y8c", "315ab2pw5xnodj6nb2i4mdtmy2wm", "gvb1orrue6fcd25x9q7e2sv7t", "31ig5lrlziswvin5lgzpnptqmuya", "31ra2xn3jaw6sx5o2bvrx4bhpb2y", "31v3nk3vhvgho3ixgdh7fvwwwdju", "31nzu4ffq62xf2jkoa6pp3tu6uwe", "31odfyonbehmxe72wjfkgfvprlo4", "31hyejoyx6cw676m7uftlo5lm2py", "31gjb4hmbyi6upy45a6qoymct4da", "31pucavv2wgrea2yjuibnktuvd44", "31svglfojo4pdgjzg7qmzmnlejeu", "31lqszhczzdaoew6qqgf6qmpzwf4", "31fggzh2prlugv3422i2af4t7eaq", "maoi70ghyr5gbk6grxw171ax8", "zfh7yk758t07xele2fjrtxly4", "31mvvomfj2vqjtp5zldhs5xhklau", "1pdrja1mx0zkgfbuupyhmwni2", "azkazahira", "p6kvvm66i5k4o3alrs5qbpgbj", "31odybzaej4le37jxjokk5k4ajse",
             "hmo3cwxzoyezol290xld2f1ml", "31riqggtfurugyftql44zpuk3m6e", "31diledb7c63b723psni4uznmxae", "kqfgjjhw1akvtl1zv31d5xmro", "31twf5hs72ojksvitj7zghj2epr4", "p0dcu8e5iozg2dxh364px3uk1", "31n2yxiqtp4x6emhs5d5ms7zw3se", "7pzy25m43fb4dbemxttlljuql", "uhx3sl6fqgrgtr62stywqsxyj", "317vh3jgcgtt2uxa2odqpvzvnmva", "31f7zbpqpkqid4f2yfdy2h6hwwaa", "as4cucdntmq0ncijh1dv13cwx", "354m32dty46av1kj5xqboi771", "31epdtztvallfce2xwuzyj5sacwy", "e3bzm2ijo81g3lxz035vesbad", "0m6hfvprl3a3tamv8ewmkpntd", "31rbewrt7efeb4qqx6opeuugrpcy", "31ycoud3nnwlufpspwdqkwumuln4", "rv3zdxpegrf7r497zshsse0tr", "31jvpwuwusoxlrdpqoq4gms5cj5u", "anandadini4", "azyjic6snmi950lokrijaskkz", "31oqi2dawbxr73ydk4qdzxwmcaqi", "01pi4zlqpk1zps08grpcabhgy", "31c4bbow4tkeqyb3aga6oxtv4gbq", "w6aw12jgwye1h4cnzat0v8s2o", "vy54g0xyuu7r5x9wjw154zorr", "qsiy8h8syggdgd2b8iv2m3uts", "31boftbonqv75o5qyxylpi5y4iue", "31wfkmvsemun7dxtu6eimdn6g46a", "31xca52hj7gfeaq4lsijl4xtrh2i", "7bntwjdswpqhrnqr0gssydbd0", "31k54pkgikmhu7ajbmkx2dp5zxpu", "316oc3qn4fd5z33mhyv2szzik7my", "zmkgs5bw25qtr2zckyh29892j", "31pm54u7cs4nnmzcdy3cdc5wiiuq", "ski232ku7a8odhblxzs6k66t6", "31cbxbofetfcyo7o5hupv3nf2qv4", "2uyec5h45hcjic04kiv3do2f4", "31gdaolhitwaes73vadcjodma5jm", "ou4qmx06pg89yvrft014q0hwj", "31x7avoiu2gketh6fo7bdlio4dfi", "31acdjxzylmjp7b2fiorirafnuiq", "w50f8f1lio48y4yena5rhz0hr", "31oqr6ccqgzm325onl73tuemd4fu", "ae65iyswqp6fwbols0g58v5z9", "31w3vmnpvnhhtlu2rjqzsq73ec3e", "q8rychhep3wo86ryqddm9ox3l", "t3krltomfdbfn8guy1ndc2y2h", "14lh26ox32pz1g9bkria26bvj", "31tzvm4t2cpfxmvh6bjyzzciyviq", "31tznpc45rivato5ima7n7qkubhm", "59xk8c2nh8dkyyd3kl6xtrisk", "31tqkojrdanbns37dqct56dnjdsa", "31xcig7kzesgfkinil57ggjmgu2e", "rydpastin4o23hl5pzh5jnk2i", "619hx110bq0euhvzc8xt2izd7", "313xxlvqbzjca3zqbyatan6fxf5a", "31tll2iyjeowucxf2m4qcajnnh34", "316zprr7gltvre2jd7svsru7qy4m", "313ijm464m74npcybd2c6t2rfkzq", "313dqmc2q3elz2gxtl2phhmsxxay", "31h2paqpa45idvlxpafj5slywnlm", "erw2iikv1lxmut0vzp4eguknp", "31vxvhdtmkqob5vmi4xdfopr4nlm", "bwhqnxan7p9e5sc9bg8rxs1nt", "mgmqh93kf526jsxszvorpl6c6", "315e2l6dppaj4om7ysun3osr473i", "21gsrc35oj5sfyvq2zkfqjsfa", "r8txwzquzwijspt1a5tsx9q29", "gma1mcz1vs6s8l0z5axapw1v9", "hkped2060tcy5sjlt88yqj33z", "31cdvkdxwmjtzvta7ru6v57ady6a", "31r6rj5p6oxr5d47w63ek3iav2tq", "31zyaeuqzw3u2gi2z7tvx5mv77yu", "31h53coslx4jle7gnjdfwp2m3h7e", "3yrmad20f43u3tsdso5y1v8hp", "31hnff3u7lajke5ysmourrfjbtwa", "31pzy22ghfqnm4d7avlgwqvjk66i", "31leej6zgfebzub3g24f5wst7ghy", "dygtyv4bqpztoljie857i8i7q", "sun9ozmhg7y9r9yzu5dn4o151", "31z3rvwckbs6xt3srd5zw5tpiave", "3z1swo9zojhc68mdb9ramdull", "wb09hvocyvva4rmrga98d5ql5", "313hyii3rfifjnfigagn6cnzh7sa", "31rzffk3qtuye5g44rynknhabd64", "31gr7mocmbtwedzxpgrdkwepyagy", "31mfxs77xqovxm2vhqgd3ttpxr24", "31g2i3fhud4u56hcwcgv3fgym5lq", "31nstnexbv7ym5yaqswfh2akxixi", "richrdkurniawn", "31xbug3marbce44smqsh2qok25my", "31yqo76jobuvhiht747xlfqhmlqi", "ju4vxz80tye83fd7dvae72ejb", "fwl85rhr5fompz07dtytw9lyk", "31645cygprifcxditotcjw7t3g5i", "31lucrzut6yfdqg4awdb4xqi4clq", "07bcn3uq08wdztqa5uq1nm5td", "5zp5ctkgj60u5wch89046bpta", "31ittyh4n6he5ze5jtftsdc6kf2a", "d90n1uziilffbez2p4nt0103s", "31jee2zubg6axdly7cyne72logym", "31gghy2yt7ohrtdsb4qgynuhpbly", "31ugyo4y7wvsn22h2guj73idwacu", "31ohefa5xa32sd3izskkovsfb52i", "31ge6467rxo6oibfnu6cb3yi7vvy", "31wn3adyeqrxlowq5sphzi2znv3y", "31y7otq6jnvgck5kqwlnw23qngn4", "31zezwy6qyr3y7c2vjma7fhdzttu", "31ssvgvbeza2kztgwti63xwn2efe", "q8b2bytmwsys1em6fxp6v9b2m", "31j5m4zqvijuc4fmtiv5ajycegim", "dtur88yby10qri7544ui93aak", "31xijocksqof7cp37k33u3axxxci", "r0wedj74zcl7zll13z1nql84z", "ayke8ec7bnr7hwouxcfidj242", "yd2uu0t0t74xmzh0oswpbbrkt", "ybouqmyr91lr0j76ld0byu1yf", "hncirc30sm9hkpxsr7uldwxqt", "31beewvopbjgrhsn6mcfxvxe2uei", "kniohavsktj1nu6scwy0pa3wu", "o2jtrm6vm5h2w8midy0id4ru5", "313su5fpioeezkgal2mhkvmhezta", "31mnkg6yv2nkqbjgzhvlujuarboe", "31v6qw7sxtvej7nwaotzovtxhqdi", "ap4hioyuckudoh7k11urkfl4y", "87ee9y5u4v1uzs1ord565r6er", "31j574oh434d2cx2dbmo4jq3bina", "31sjg2binybh47e5jg3oxtjhx66m", "31u6d24fs74nkbf3cxcgfrhwdexq", "31lfjiuowkfpvbpksuhavxdau4cu", "31ecfvgoghw25xwv7klhwk6kdana", "31lhymkk4goerudjznfoa7l3e5yi", "ass2ad8m3qwhff835mkv55vck", "3137dhyveewl6kz5s6qstnvn27py", "31sbergwxkd5wbsmrtqyfhlyyun4", "31yp5i45q7ibfsjslp76dw4lfeu4", "plrym7wj0flltdzxb35ucxky1", "31xtnlpta3xkhg6mcu5r6nmzhnxa", "31qeks2rj3auclfyfqxtazgftgi4", "vhemn7bz69e9298j3cul73ujs", "31z55pbi6zanlefy7mesk6m7wrk4", "8j7838blgtqb5a85ztejgmt86", "0i3hid2hsswrk7vnxb6cpsl4e", "31cjxxmuzw56rqvd4f34rzd3xi64", "b81z7jno1at2h3hujkzizmdrt", "3163d4ibi3eqhacbivvrvdy5dlci", "31tvuza2km2v5tj4glsbh62qpqeu", "31jmbsnh4jsdinyyavq5boo2v7uq", "31ehk7iom6azvyaurbfnz3dcn2je", "31qki2eowaodbynpvjnxaubn3jxm", "3lde8252nxvll8217wvw38vr5", "rcelnre67j4rg795pjd0oj1bx", "31erhzhlgk5z5ekz6qxrf3zk2m4u", "31qwiulyhi3sdwjyr6oqgm5l2onu", "31cl2grs67pb5xaept5hkn24xblm", "31khl6fq77jw5f33aoef36r3vddq", "31huhphubsutf35ijbiw4n6jmdn4", "312cj3vo7ha5llvpwhvy56eaanre", "wh1rv9pjueqn7iybla1mf365w", "31fjg4wglvfdzhqye6icrdk2dxtq", "31f4lypxyqjaiig5ca3p3au3oxrm", "316rkfvf6gh6mvr67wjmvdevnqpe", "31opdfomxemyqt552avpl7zcxr74", "31emw4kib6l4gqrrp4ea2gm3f5zq", "lpxn9d5iwg4pbhq8k2ihm2nmu", "5eukieegnx1a4wzq5dlrsio1k", "31hmbz2fp5yllxeoladvl5o4ku2y", "31iggmvzctzmoqrtlj75hnbilquq", "316svpby33scnjhgpavpiiqglpxm", "31djplgk4ge4h532gsehva4mqh5q", "4kd6zk1nq6vklfitjif340jtg", "z3qw2f4ro8ja5i8quixotmkwo", "31mff52smqm62mtxkg7kbcqdcejm", "31r7e5c7cgzmznahxmvbre3iddjq", "31tddbfftm6rccexkiuc4xczmf64", "31tjhmhymhctwmm4emkkxghkqeoq", "bucb681qst20j4dl15ipb2xvm", "31gjufjtppcf6g3o4cevydwgjbgm", "31g3aiq2xzvgeely4r53arj6j2sq", "31ht2pzisijkxodk3uoew2mortlq", "a6liq6fpskkr7nbpp12g0w1qz", "tvukhpsrsit3bp959fmp426v9", "u5aqlh63bs4uft8ej10ngh9tx", "313gz6d4dmexn4zybhdgfb5zh5eq", "31hdwxv3ioicjkrujgey6ugqd7ey", "s8uhn01n87902xcvjdimkfud6", "y3iz18di6xntxmbgad9bju66r", "4qxqkazvukl5d5oefogg6czlc", "31tx2wbxwjo7e73exgl2q5as4xha", "31xpfcz2fq56sahn3pyoina2wwyq", "6kp4a8ak6u9x5oku0d7ish7nm", "31jln5yv3wrystjyfujhtvtizpiq", "31swjmyhkpdnskzwd7tvytklbfey", "8lewms7bzabvvnivp8afc4j2t", "31adzzicg4prrqyv5bluohajvzri", "31c2xv5ykq4tje3dlc442wmotkqy", "31slge2gh3r3qn5lu6yzbxt2lmmu", "2egcst1px76wcqurojpr8eiqh", "31fi3em22ipnpoputnuwynlq5kom", "31ram3rgemablu2spiwksojatsje", "prel1fsoq125dj11rkos9kr8j", "31pdy2bb7cms7636z5wvzduunwmu", "31wgnw6rb5v45qidb4ooimhpymzy", "3125ec5bcdd2qier4ifbk5e3om3e", "31fdtyyg5gjj5thd52xp4uezuuim", "31rtsclabiweapz2spiqnlxe7ham", "31xpdsrbbjqbyb57uiqdtzxr4eze", "5xm1lfo3axv9pazdtjg2op8iw", "31as4xfsbdqrabiampce5dtkmgvu", "xuv4fed3nx85yo7bptfa87c8f", "31ujggpcykeflgrv6i5wwnhk2sci", "31fe7g7tbx6g3sd6cxacteccl2su", "d5ia7z0q2b12uy9s2mubpq01c", "jgdgyi0rto3ev7ifecktf5qvt", "31l7lgcg65qy5w5cectouactmyf4", "31n4hrj3dnabnwgxqwa23ema76hq", "9y3pgwg89qz14ucchfwk7l0va", "31ltzo32akgebjywku7kljmtruny", "1g3nzpqwfq3amvqfhxdd3guct", "1xwoe5qyzd8pc5ki5fjg93lvn", "6xa9jwjjf0wm5n47i7r74udzh", "rifatashim1712", "31tmyug6bnzi4atqccwja5txmpra", "315naokjdsdkfz7uf3vvkjebqg2y", "31zwl7r253ymcbgabmxsjefb6mpm", "ekmcivor", "316kivvmcropgdp7plju22x6gvhm", "31ivk2u6zu2ud6iqudxwzfbal7yq", "5nwsg16pbz8pm1jm1cakv9k6w", "v611cue5alllxe7hq84llaoju", "31g5hodxb3vschguav7xu3u5gpm4", "31so3xzxwqgflogodaojjogczraq", "h3j6cmwilw2wfi4zqcbkyks2u", "31tjtjrefrtvfg6hmrslagl5e4aa", "lqnvwz7muf8qrgeu0uad0v2ga", "wdxdq0p9rnfpenvq0q5kmjzrg", "31inr2exoa6ph3d7wmjqo22j7vke", "31allkfgo7h5obuz3vvbm35nbdf4", "312e3yhxf3rcntawq2dux6m3qe2y", "317w6gada2uawou2yhrk22u526ki", "31isxjjaab7yvwligqbjua2bszdq", "31flbdlehffto7fs5ktvbja72enm", "31elhcg7yxqjjyzqmj3okowuixnm", "31hbhhc75j2xxx7bk5ceom4azdmq", "31mxtcrp64anqbrirpctz37trjoa", "58grmhammx6s3cbf6py2na5la", "31ne67g4hsccp7faaxkq5o63kfmy", "31qz4jxsq6ekk44w3rftopjexgji"]

try:
    for username in usernames:
        playlist_ids = fetch_user_playlists(username)
        for playlist_id in playlist_ids:
            process_playlist(playlist_id)
finally:
    conn.close()
