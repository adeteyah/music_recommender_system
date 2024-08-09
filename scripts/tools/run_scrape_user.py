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


usernames = ["1292600398", "i6p5tb4w5ywuxetjg8y2v3k9z", "31toeesr6tbj4moiylltqpbguuxq", "31galwd22ewdj65w7zcjcwzu3jn4", "s7k8oamnr3w5g2rr6a98vh6yx", "srluvymjplbpkrg1a17wsy9dn", "vtdjajo5pfjh5i91nm7ohe70h", "31puyycjkg5xenssgefh2xyi6lli", "314o2ervp3xrxs5bw77wcnomg3eu", "hx6mi6e3ozh44qcrpvfysssri", "31hgvvsrhh3ad66mhttql2z6xgne", "31tlqt22dsqxny34ze3rv5j5nebe", "i6p0ydyhsjrofawyyan8o7csl", "myxiwecc9rh69ojo0fke96nna", "cri8luo137o7bzlec579kdyve", "yamr6d4ip0ogcqih9zmk28xpj", "32ysusiiib3slfl62ry745y00", "31irrrbgjtztq6waisgcauf3dgte", "nk5x7qpln3csd864sq297ffws", "31ri5aiw35xhdsb444qqr4a7zq5i", "31rhdyu32fcpgfnfxpzst5t7yoau", "316tttk7trb6js66bxh3c227mb2e", "31beoyjvzqe3niie7mi37lctszvu", "d58yd9l4gdwbwwlss0s42n3zn", "9dsf9jbdxm6tir4y1e7d0sorg", "3147ztqshi5j33kijyrhkvmzh3ki", "2yqpozbxo6awn6bl5quee9j5z", "31572dnwl6qwsaupakx2vxygiooa", "31qhg6rr5ocwcvtfxqmh6e7vrcim", "31lt5sniq6pv3udenwr36ymrjn2m", "hv71kzwc6bkesppim6jte9ep7", "a395erh3qd0hit6yv7txltsy1", "31u3ijsuja44aneihsg2guznwbce", "31u7u2p6frowsyvcilngaok4mzoe", "31nstnuo53do3pzqawjx5puz3sam", "31ggxy3trgxqkzmgucnp2k7elp3m", "x61vcfssjtqu6fsi7k0pkgmzi", "3pjek5924g25pq7i78fxcu71g", "21jkxwtsuhprjjs4vsv4tmbtq", "31ej57yidxz6cqypakllijdnnbu4", "31smknuv2dewcnynkg3bbsceluhe", "31fwmv6so4mzvtogsacs7bkzrrly", "31yydncirxyeac73rr3s4asgdj6a", "31uileq5qbtgcikphrbe5ucxo6eq", "l50ivfgfonti67yw6o78a9edf", "ok4846h7surtsexgixnroya8p", "31mdyzzeu72qtqrxxmrg5rbnpxoy", "31svn2q5fqyoy2e7iql4gligdfgi", "31pscckyax72vdvz4ppimnpljgom", "316bvmesruzwtz2gqvsm3s4h5g3m", "31fpcctbthki5a2zfyliqcgl7szu", "31ne67hox3mckd26wo5kvcyptzje", "31lf5hz2edzkubjz6tkoteg5zwhm", "4tgdhlync8duqjppgv7ddqc8z", "86cqijchco1dt33oxwoqjxcjg", "td1dupv9b41k1cws3uuaxshq5", "31te2lgb5ejgwhztlbyuiyg27vam", "31wct7yf2uwhfyxnj2x3s3sofcoa", "31ymuf4e3ketijjpofpdaklbqoha", "31ewfsazwim7gak7intvm62v6tqm", "nbwqxyiqyde6gg6qtdlmwoh2e", "ldyu1feykh4irg295ulydr0jc", "31my657ebw6rbt5qd2lmnokkzukq", "315mg4dhe2q6jcmual5zsf65dwlq", "31zkl3bkveznpeqcn2umd4ibdzhm", "31lfdlmhtxy7ycc5myxg3cdmcbsi", "v6vr9pt3yqrtcotinv4uh5gle", "ut5zxjksm2fl9kmueowkiub9s", "31ydqfrlranyga6zlsujxdovp5ni", "p75jv6lldo50sl4q5nmwwq83s", "31k3o6uzng5gevmdaa3crlcrqbs4", "31dzbmz7qjnea3ebvee6ww6ezqo4", "316dkglnk425h2oiyrp7k3ody77e", "31qoe4ujcshtyjfpz6myskykf7wy", "pfrzut44ax304fv5ls03x24zj", "1oqb5rursjunf72v3id1ab1ce", "31tjoxe76t6rjn4h4t7sje4r3tya", "utquzmewof4gzr4qitc4r4acn", "3166vplvrn3odab5h4khltg2rz3a", "31su5pc4yevamylscig5fya3zjda", "31f6wrkqnl75ubznffymg72m7uui", "31hkk5pwx5amzfirsfouushymx2y", "31x3r5qlhy4tivtfyqhpwhfcdyva", "qcleoizvbx3nkto8fj8mhrhzl", "317kkue2s7u7krhwqbrmtdojqwk4", "ue4a0yvenulvhvew8wh6kh063", "31icdhmm4qg5qochfj6bi2wamc5u", "hgr2wxqfc190gvsembnguvpfd", "s024yin6rpbiwwbpj0ibxqhno", "31mtyzl3jh55vqtn6fkxijogbwmq", "315ig3hzzjoyf2orfhn3ewg7zrwq", "31knidxspstgity33dq225rljawa", "p27k18l367933pd2v84iq96sq", "k60cs8u1psmc167qd7znm64tk", "31irmf7o3nsjofpr4pxyda7hpwu4", "tjdnrvpoa4zgg4v4mhthwcmys", "31iqpiotejcsgiaphgi5iuurwd5m", "31dgzoffdvzspc4fqent432qt4nu", "31c5x3vkox5247aipuff5zqylm5q", "31skwvyfklznwakrtqwjnzymoizy", "oss0s8lg5cz97qz3o0smt3ml6", "31zwl5narv4msfcvjzlgtv7e565e", "31rqjm6qkiykyrwg65of6czisnde", "31iebbajmzibvrfhmqww2l7d2fk4", "7v86et3rh3xb4sm2ja11tq0x8", "7vihbjpp15b5lszjuk2szu7jn", "31ri2dbn35hjememofo5au4svduq", "gi5fbnzmuml5uusenyx9njv2h", "313gn2siq2nkaqspkr3bfguvpyva", "t2ptp74c739ocnbfgrmtjurzm", "t4teanpfoiyrn4at7mctazhw4", "609o4zm58xtcrobfh57rh68k9", "firatkaya90", "retrop246", "needforspeed", "31hmohcjxvjeqqzkjgoivofsvgam", "xxzwf7d63usathfwo95u6wr9g", "31iwfhbcvmvuleicpagoeck642ri", "0gdu7h2y1p1r27sx5y7wwqn3i", "31wbgaltexdcygzmqkh374ds6juq", "31kyuz3mggyuzp3as52fqdnswate", "31pdg2527ioecocl43ztkglmtnue", "znvbupms1kcd36yejtrav4nm2", "lvkn3ckb6526ruacejeipigol", "31jgxohplj3vygxf6ipbhrs3aqua", "31deauj4iqfdehatwpdz4jxrsp2q", "31ecy5yjhv2cu3fptq7op5awjzoi", "bol4t3ys5nk3p42wto27p94cy", "31yuz4lh2whsqslprvnv3owt7cfu", "21cte7tj3tyan3xrtvgjykdfq", "31tngmlvffzhwp6fvlkghzbkn7wu", "31rtitfiqnf34pbeeemqr7pxr2hq", "sanik007", "317ul5ye4dgawyhaogtfhr66lyfq", "31urdrmpzilaxjm7ryqpzyuef3dy", "31urupz5a6pfq4ejg6mmrf4ugevu", "31t3dip4tprhbhrnu5h6rk6grhru", "31jmwgtbmzx5puxz7rl2bfnrudmm", "did5q3nriq523xiww8feuld55", "q574dkj5bbw9s83d8krz6rji0", "fakgpjsmosqbmnr81kutz99i3", "31dgu7qx5xb4gwaqshnpfvbsvbhm", "31cwgyg6vqvkmu6jsh2qthitqmwu", "kuiwddz9ixzpbl1quxojza40j", "313eqrouojucsvw72f3gixfjcaay", "x4hnjxx2cjtli2bkemr9qfhax", "31p5sofwbf6xfag6jvaie6w43ice", "31pugsla4gauucuc5wfsp7xzke7u", "ccrscsjrhnpufdpiwfbk9jfgc", "2o9f66yea8a3c2xorbw115uhk", "2a9ld0ufpitucslpgid16guoe", "31qqqotjplw2kf3rdhdalljxinsq", "31re6my5axmgbnr7uz3urcdiqbsa", "313j5kpwucpiemtdo2wr6mujgpgy", "31cy7extfb23ecxb4g3pullzrlea", "31y3tc4nfw2gnvyy7k6jflf3nhmq", "koqz2p6n2aa5jrw5ab0ye63sv",
             "31gxpifvnnlybmzflwmyz3b42nuu", "51vzm3i0w9v083phr21p6m1a2", "azzoxws9t0hhi2swernicvck7", "31up6dac44z6alrfhk3sg2avvknq", "31ckpzl2onkd3vb4s7s5o7dx3pzu", "i4w8424dyp046d7afwx75f5q4", "31txtodcq5rk42cmv23zj5li52y4", "bimv4g68yupng67e70lzebkiy", "31pdhigrrk5t7sdl66eubgeszotu", "31pp7nq5tezk2jxjb2iojyxfneny", "qhnvo3bom4dvkyzw9gjhentwl", "314uuuyrt34g6yd4lota22aqzn6m", "cyywd15mc6r8ehzynwdz1f0yf", "v9eyndmar5dclqs2fi32p50x3", "31alu26xzly6slclossrnmco6izy", "31qmjoqpw3kogaw54mcpvb5k634y", "3163surfupjtbezpon433riju654", "31unwzmelffqfbrajvuiyk7lkjeu", "31pgl243ot5rmlsclykuilwugqhi", "31vyqksy3lglbqappqroxwbwn6ne", "7nn85ns2xfub9eif5t5g6kptj", "p9xl7cgqeurm0koju51wvynju", "31pll7djmcx45arajnssgdjh55mq", "31b7hl3y5dlsc7fgbxkjdsab3tn4", "312nmnb2ebr2er5wrivm6panamdu", "31xx2pyudl44pwarn4pidwy3jvvq", "o3gbpul098333bu75sj2m9nlm", "aygpb590ecbqr1aqzfgr50sx7", "31rjpq7w24uhp5hwhn64obg3cj6y", "31mem5ry7l7s7gch2wrkgeyv7jpa", "31yqiwjnzlj5mdjozkacvlppqn7m", "awj5fxh4ih3mq4nxx3wt2qey4", "315fv4go57dkjz3bzgtowdti6huu", "31kuqmrp4y4qlc6unmahnfbmnyty", "31u7dalmxf2q6vmd7r3h2mlad6ay", "31gkowio3zyg4f45bri6l4t2gutm", "31fbnvojxj4zveuouxojaoagp3m4", "316l2dubvh4oa47fb35duezcej4u", "zmeaa9mk2aunsunvtrkhn202l", "31apmedypeujjvqqa5qb52nokzre", "31jgkq6gxsnjjikpl7fndttr2t4a", "3173iner4b74nszujja7od3xwhje", "m64wdycqz3v5w0tpxxvnp7iqq", "31d2i3bxrkrkn4gdzoibsgtytfr4", "31llczf4u7ikmxefn5m3d2i2csqq", "31lp4ib536ej3ap34evznauk2c5q", "4l619xec0kn5o4o97x6do6dz6", "31tckgf7tbgk6soliw6eqx5hkceq", "31kicpvf4byzj76hf7xoddcj4vaq", "31xcm4m5gzkqroixhs3iyajfu77a", "31z7tbqpjvtomghuquocdpneuycu", "31ims77ozszzvoff75yvf4r2evde", "le061su66ju8pioc6te3k88zl", "31uythzji3u26ikbtxhjqav4byy4", "rtmf440t2kvczvtvajd1lcf2d", "9zmn5q0gbpb8o67aldwj2jdh4", "31tva2tdio66gayaopbtpviwe2ba", "21sjnzpyi5h5lrjmywe6dkyoy", "hwulc1kezw6xrk5oycwbjxabr", "2sywmcjykb2v7c7l2omnidbu9", "31pxtmmr6mvx6tkyominwvywvnsi", "31ke6rcyadhckt6qi7yxocixb2oe", "31lok3jrzkaleq336cnwywuv2v6y", "31ksyam5uqvksttjnb47ynplcqou", "31foxqbaatxzkt7pksd5tdunphim", "31fwg6xqjh7apfo3golgtq4gvb4a", "31gvg3ucujf4ol462uc6e4bg2sxq", "31rknbxcn5imiuffeue2ismgrw2y", "gi6fc39qv2zsfbgm1w7xkieb2", "a3xqbmgb8uwj60x9vd31ozx8a", "31wytn6kbdp5e2avqj5uozaplbea", "h8jwsth76go6qx880leuzjkxl", "31a7ptvgf4soqbfhiqga5lai5gxe", "uapi29ctfi42udjnyfo6zyp9x", "kbwj87lctm0hf024r9lrkdabv", "nk3bvn0vgt0cfsfv28is6avbc", "312eqwtia7n6uu5pibih6h7xmuwq", "314upenrcql4imkztgk3tff7zk2y", "cz9wd309f3ieleibpracs31wd", "1ybo3y0hwc8ev6cg8ade9xs29", "31askhrpzzvwazp46dhcjoxjp2gm", "31tyblqirmbimqugny4pvp5paumm", "ra3ll36ekkt28xva9g1w520h4", "c6sxilrd88i22c0ekpy165yn6", "yjxjoqzqm6lt7prqsh9aquxxc", "0jddpo8alys15safkm6ptthok", "31xq6jiirq5abfx5qu7kz5232knu", "31ul2eaj7nhjteyjn6banntbscqy", "6dgs0w1unz1pz8ig4r2mi8m9r", "31oklahay5xvu7p3ucz7hez7q7w4", "ivfzb45rfbjxyoc18am3p3cdf", "31sq72fy632mtdxmpan6ctjtdsgq", "31lzhsjfpa6ikyzzerdpajfb6jpa", "helgrs1p8s7kx98qxcbx2lw04", "31376rin5qfzda7a7t2iupgn2u6i", "316nlfa33m5dx722gz75t3wukeka", "31bzayzzfxikinuvp23gqdytj3bq", "31ptul5x73ezq35n3xln44mkevvy", "31jvzuovhl7tddsfcvo5tg33uyh4", "31hq4zk2wmd7db7e6xwqkmu64aie", "31sfjylzvagaf6vi2xbiakea4fha", "312rp4uzjssdb4ci7yhn22o2fz6a", "5t4eq71x6z4hw9rspx3xyvueb", "41svtyfuoc29h0mjzx2gs87zy", "31pocgszvjtv4qpmcxkztjeei6zy", "31rvnoyhstrjixg4lf56xyqbsxdy", "31wmc56anivrjjyrxx4qrikzihci", "31omq7yftqsz7mgcam5467y5senu", "31p4rggi4yexcvsim2tnidy5gyxm", "fhzil70iq7uonnwmuikanh54s", "31ldjggq7dffc5fd7b5v5gykngum", "31kr4n4lw4gjvixiy6jtawbceg6u", "12143542887", "3132b2t4h6rxbayw7udirgbpdyba", "31lbwa7hhzf4ce7ceyhldfxd3fom", "cgg0skpqzwd414xar7leoe6cl", "31ycxjp4f72q4zvvdnxcbisbprhu", "rkpozlg09l4b2b1v664kf0mqe", "31wa2nklclfw6e6saymhxb3a43di", "31idkcuyf75ck6tctcv2pujdpewe", "31vawrvumuktinymgkdclj6l6c6y", "313mccy3ncc4kafs7i4xnriukqmy", "3144hcatrhalacnzzrb5lm4kp5um", "6zqojqgbwyam6xn3mai90sf66", "lucswioxo2ec9d9oopwst9fm6", "mnktqk6gch6aq97aawel5iqn7", "31fbrhaphhakybvsrbzjzvutxc6m", "31u2tfvv424th7be4cha7rwy2zly", "31cdtm7zvl24qnkozlizry4u4b2q", "315nzoiiehltyu6gequ3mdlujbwm", "ktfawpyqgpzl1a0iiz6m6c6h2", "udydakfspmuhr5yjoe7d4kh2x", "312ra6n3snu4qdbp7vzhgv6kgkpy", "31p5vcjc6etlgeysor3wo5ixmpw4", "31fwcghr7lzokcuna6s7js3m7dom", "31bitxmpjqsk5j6uiufrtvipxts4", "spikfdbtb5e9pbhmnk4fmhxwr", "31jojc6g2p36wkhu4t5dfhb6mx34", "31mbup7xkst5mckbm67fkzkex52y", "ar6hp1tebjakhknwxbwupjgtb", "31yo6ohsxqipeohrwamw3pkgu3la", "31trxizhfghnyavcrdjysrkor5ia", "31ylxjygzhuin4zf2ptxugttz4ay", "9f5t66tq8xuf9sm0ry3gxbgan", "31hdsx2vwojbxtsltyul4d2fgw4e", "316dnpbbctlr2ng6oxdz33s7gcxu", "7dhuxwoevwnaoscngirypiffi", "31enp73lcjynzm4ediodfrzzylee", "3gvckh0p6a4bzj9tu6850vpv6", "31qj5hiostlkj7on4hgpfj6veple", "21rut3yvaguhha6xnujcpcria", "o5gzkwyepddcfzalt149guq4m", "710m5r1payq5yrr7nseypb2gf", "ca0kk154hzm00uk5ornkm4zsi", "31yz6jcnynzdk5iz3yhmy6zgbqaq", "31fbec4xv6qv67mt7asl7cnwze7a", "cblhx6lh9q7awu9nwg8jjpfu8", "31nb4czeqiklk7b7gw6p4apw7jpi", "gnyfn9kgg1i44drccf4hy5urd", "31nsv73uq6rx7pjj6zlwae4oe33q", "312ikigvy757ze7hcnedokbh4rny", "vf047gbbicjfto1or29hkrsxu", "ujgsv4avs0dsq6eh6g486j9jo", "3156fh5cvawhqdphxwwpgoxcumoq", "ggcq6oigpov66jlfp40m8vukq", "31giywk4agv42hpq7hthdrgjvca4", "31ixyjc66jzcvsb4wkh5f2xqcvhq", "31o2p7nu2ft4hfy5ovk5tzeb2h6e", "t5f6vgks1lipj22nl5yqhz6vg", "1nxgz635771i1jxwh0g42glsy", "31oiyjggeohmz4y66liuarr4nzde", "31va7mz7xmsvbiihyznriun4qbai", "3133i2zxyzfzn6vy3mm2xx5hq77i", "31xhi5ffvjbwjeofl5owrq7oexve", "31bz6dpthmhyrl2tfbalz5ee3ay4", "31nxxxyuqm4tu3scbti5w7tmoila", "yv5fnhltar4z53y3gk5e2p5yf", "31tiho72gay6yzkofeg5pdm2fiva", "31fdaw7no6u34is3ktrulsitzgmq", "21v3bqtbwhcbvanwrevrtk3tq", "31zmvc2kw2g3nu65t6ovwycl26n4", "31twhjt7z3iw7rfuva5ox2jtl3iu", "31toqobny6ei7546tmyvvz4g6ysy", "sodh59zf7pxj0gdjibjobgen9", "vontg4rrmyrmzp5f59zou6cnq", "313oxdm6lkb25of3xvfztjdv674i", "31j4hbrc36h6zxlv2qeqwk63wes4", "31shp3cmyq4dxfzrwihng2otflji", "m17k60er8grixkf30u691szl3", "31nvoqx2iosdttdcczldrh5ks6hi", "yu6crytipgm3s0flr50jl5fy4", "uf4uvh2xh73uvnv0ebvtmak6e", "312pnpr426x6qckogofjz5yznzwe", "vxuujs5h01cmizqtkhqeqi4dg", "31goea3sow5pyvchoi5cbx6jfj6a", "31ltwjkrqjxubtmjy53ko7vt46o4", "31jntoqocakbk7jal5jcg2zt37me", "po07ba3xzoev01btodj8d6ww2", "31qf4q2kvquonglf5lh5nsclr2iu", "d4k2s80mysjp2t1exap8j2ski", "gplsfxur3hhrrgiipqwfnxjn0", "314inzavxlbbcauh2q4yf3qw6rsq", "diqmek2k8pd85cy2vtezmtl3y", "4abla1rpwl2opwjppo60aload", "31bqk35iba3eaw5zosquvzcbfmpm", "313yepwqg6xg6e3j6tgrafw34baa", "31fbtjnszoud5uuikah37iprssqy", "31mw2r5exznxp6ebamw6tvcpu4w4", "312qsu5nzyqsz5ek3qh4f6jtpcge", "ubtiptou5yb4kr8x5r09m97z2", "p3xu49ruf1ce8qid9jgqmaowc", "31h6s5mrdhr6xugotqyrcywdw6tq", "317rsotraqodp7erxc5o6ryusrzy", "31iwziwqjhp3b2koptcc6zumfck4", "31kfhotgpwibhza3crgkgqdqjmwe", "31skygljx4rsnsw3f3ht7sghakdq", "31nbkopbkcugjp6j46wdp3xoz4uq", "31zqzgvxjnv3qygwy7xcacis4nca", "31dh7sbe5cdzcfnmh7lnkkvu7wn4", "lri7cbokx2bjyuxy2kavyd78d", "am80p57hiz2un1zfzs75va8wa", "31ddydeqjt7heoh2lpd3oj4nntf4", "31hm72rmh3q6htbeaea6wtdn3a5e", "316lqgdv3seif6pi2kxncnnoylfm", "vqs5bhqqlj8ant0f27vguuoim", "inkafad", "314h3nkdo2hr4du55emgpku4b2c4", "fj9dpi5imk26jbhe7339kfmns", "pskh51uyqk7qvd3fov7a6lws4", "31nbr65t3p4edyow3lgqrqzapdja", "cl8idol7dgsktduzlkp4td56a", "31yba4w6zoxgyhg6zdpzelmvgaby", "5fuhz1lsqj8cfc9watp9tpzia", "fqmv1f0pzdyo5uftqgb24x0h6", "uhcxuymhrqgpb7ssntxq1vn2l", "hxssv0qzmay6tib1h027lugc7", "312wfyt37qrrkf6ictx2g4r6k6xy", "31g7c5hj4bltlo4hyi4ui3busrm4", "31mm2nvtjple3ta3qucsjbxtsw3y", "sdvg0pggwlgqwu49efnzakdfk", "jqca6s4twtcdn2hmzenbmjeey", "31ldkjcj3kjottt5omujj3vyyi5i", "31e7gtcppmfwgub72qcnzuhtuuqi", "31geipjqxtlfkmrvwmbcfimomsta", "31wslskrhfwnr6ogbkb7nowaxy6i", "316m77u5b2a4pk2xi6rqlkvgn3t4", "31b3ga5mmfv52nnikpaoptazgapq", "b2ljppxc8vbej8n3mzm5bmotu", "topsify"]
try:
    for username in usernames:
        playlist_ids = fetch_user_playlists(username)
        for playlist_id in playlist_ids:
            process_playlist(playlist_id)
finally:
    conn.close()
