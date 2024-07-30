import random
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


usernames = ["31vkjrkt5jdwb3myspdnyay45d3a", "31bczvqqlwyasxu2kmxzq3l5t6we", "wioh4jl78yg93h5diaxjjr71l", "31qq5pgn5la3d5lfhgohwtb26gye", "38jsh448axrs58t41jmcqybtp", "31gnahcmmm2vle3z5ajouk4633wi", "31zmpyjcvq44mw2ejusfcwnnbtt4", "317lnnfpypub2fy2zuuhk2zqjuym", "31wtwbbdrjtpnvohepirdut6fesq", "11g1nmjhuxmmua7pybko69fdv", "21dbutcher", "31f4ygeqvi32jxmtmdqw6new75xi", "312autikh6lrnc75nogrjsssdf2m", "p5hbktou7i2jh8ym7ulgs60uj", "31poikhjhrzbweehy6felykw5yde", "b475zcgbt5p800hyt87jqjp8o", "31iontagyng3wq7fwkkqdo5wibh4", "31dwool7kqkgavi4s6ivuhwnojyq", "owr9wpz6h19imxf0x4kxtxdxz", "31u6ym24klwtfg32s4mwy3nxgrei", "ivena", "317qf4qpdmdnmi26gvvpeynwklae", "jfa9nmudrvzho9w7vi24e88lk", "31bufcwidhdwe5ouz2rnqcg2cxhi", "n8e84a1gfl3ggvvnzrmy24q7v", "31bs2xqoutyl6p7tuku7g7sak6qe", "d688wdev0r9238t1qgz0h87c0", "64cr32co4dr7bhjxk01ihmjqk", "0u2i1czckn2o9nh0crytzd4nm", "31hsuobjey3neanqc4l35ywubfmi", "31w44qxkhwtiqk3uewh3f6oshdjy", "31xvvkf6zqepwx5qgol3qz42qpae", "tm6t2qi5qrmg6zx921f7oir63", "31q5sdzww5puwx5a2uhbgvnzgtke", "31qbwtakdmmbrrhiaq6k2yqkedre", "a45dlc4s0qlf89cnalenvm1mu", "galuhm", "4k4nd9thevc8ytu81ksj2hl1r", "31bmuxtcnj7mcpui7ofqlkicocje", "zekrieldimaz", "31f7dowblu65o5tm2ytlihfpmcja", "s65445qip9hcczweryc0yk9rr", "31mv5te6hwhf7zifi3etqg27x4lq", "31kt6icnabnwfydzmfuhittnwum4", "31cmz44vkrascut6umk72753c5pe", "315g67cey7fiizfx3fxi4eb333ua", "31kj7ljb3fxsv7lm2omctz6qsn3a", "31iea2x4wmhs3n6xiufiv37um4ze", "avkk9ljt9tqu66apd0qvhqewi", "38zlwuxmzbsk6kzv1j6wq9sp5", "31vp4cs4u6u34vepj46fqdihdhiq", "lf0kshgvovom8m5ptj6kmv93x", "ajn0zipkwmisezdudqoizsnxt", "31wxvin5xepzehbzjc6sjvttzfom", "3163fv3s7tzwagxnp5zcialif2i4", "ailynnrenteria19", "313zqllec7nfuticfhxp3opahcoa", "31c6rphsdizwlbts24y7b3a7sioe", "31ffynffjhsgu4h422ua7m4wxqbq", "31luugqoq4apmen6zqeortpo47de", "vght0an6cxfe76xf2ixw8mhan", "21uqz3utp7bjlw7botrdamsuy", "31y2kso2m6srmfc7bu6dnkbba2vy", "nrklungmicq03e3zzobwtq14c", "31yd4vmv2vrmkanpm23y66ufjviu", "31kfkvvi4ms3jmybw3r3eis52kdu", "316verfzjcf4gur45uznp3auh4pq", "rzodijl10c4qaaco3vye2h04t", "39vam44v5wkgzengm1wfnfr7g", "wttj8c1latwm9rmwliaqfnbg0", "kzzdh086yxzyigqzvaq23n70g", "31eu2qoeuyxepybcn242md73dawi", "31eslpbtckqytq7cqx77hwycrvt4", "pmgbyv7epr6nn5l4mfvaarytz", "315zdpr3ld2evvtntm3io7xmxxpe", "31mfpjiwvcewi6fppuev56qqsbee", "zbtmic7c0b72u53kzquqn2jgy", "x361ainit7pfi2soasvwtosmc", "31mveny5ofhtrktqgrqwcclomg7a", "qg31f4j0or0xnky4ah12msdcv", "31j7j5qd7vago3etq7ucecnsy4pq", "316mjncwi77q3suwwdanwwagrgie", "314mlvbcjz5xmodpknqpeigfzv2u", "31q44vjdpyskdmbewpw2beel2gnq", "31cedwbocw43eziyfsnoaght7usu", "31v4fqciq5jp7ubyewbsz5xfgwgq", "31b56r43xrq75dygsojhxq7q6j44", "hevus6ftmtyh7b1m7pji1z5w2", "31g44gujkeiggofvepzcgp2ppk3y", "31qbl6zrvw4q2ibokbepvjwbilha", "31csv3uonbrkgj22o4ja233hikjq", "gwpekqnlqh9g1aqbfc4tiivwh", "clwo2eab6m7mzxugpa52h7726", "313ypoeimkjcmyd55c3owcu273fi", "31sjbbtfgiyqo4rvjuizqujdybea", "31fa3vhdf4nugcpxbu7r5lh7flfi", "31rpubnxuqn7kbm33uv4cgqha43q", "tlufgvdr7gqarp2mp1czcjezs", "31malh3gpcdn37d4stxz2nntpd2y", "31e6dikc6hlyihbj36zavohvtj3e", "cdovzng40kfxuev419z57j7uj", "31cpww7lrgjxk355njzykdi5wlq4", "igr4uczkwlm86zrw4g8c2y086", "ojj1m0x9zv071ewzzxpqe4gw9", "31yqnweniuapwg5eqpdtyvrs723y", "31bax4kq4bogdkyghklgdi7qo2bm",
             "31bkmzpi6m27ft46t7grfzj32mde", "31scg5t6spkme6rw2geqyh5x6xyu", "31untxr3ywx5wim3u3nec5f46wza", "4bjy5vi4rxwcr5iqvjgin2e04", "315sr6fdc7atmwxaumi6idxpbq2q", "31f2vairt3rqpd4flpyg2mmjnrxa", "21oom8h17g74093lervs34u2z", "a4uit9x9491bnlm3buar24jts", "49ah36obmqx75x9qaxr3lep29", "31ex3pdpvt7ksehgtsbgcm5k5fme", "31n3t3mfparqfwipshe7myee32xe", "31sj2zujejrhjko6ejblgazbhtt4", "21llwb2xam4hq5zdpnw4pki3y", "31wz447ayc33pch542eqpw3tdbvu", "315adghbr6wpoonar6elnogiqvuy", "tlifgszj6afkawp75rp5a8o9g", "316jxcbk6zv3ycth2efo5uhxeqgy", "xqpt9b4ybkankvos3wi5bpvjq", "31ey7pwluroi2jtsqicezjeh2m34", "31bkzog4mb5fzcy7wywlfvnedwlu", "31cdwcymmj6q4qyfq5e4zgw7eb7u", "onjy7xyitcbqaca4wl4d29x7v", "3122hx45banrxmqxfjjbaaqtmpwi", "31ewuujzszk6oycfvdxmocmkudaq", "x867s31q1bspux3itm15o5qge", "b1cwi5mvl86z4b7p46vmjoq2i", "313uggsz3ibdxweihs2miw4xr5im", "31rnn3xt5kaueu2qalfejkemw3i4", "a16ezxsixs1gnirz3m59bdfgf", "h85vegh962a7bj2yb4pew43hn", "sc34mio3ssd1uvbrfvpi6pkk8", "n4esbp67hk9w5adyj6tl96oqc", "31i7b27dyeqallz3jnj5alwifoda", "31rhtpkkbk5mwelkf6n6oc4fgl3q", "31ww7ycvn2v2efclt2pide4l7sjm", "31xa4elu7cgu3tdcnvnr2mnaec7e", "abqj7afxu7rxkb49rjt20loe9", "31puyjcvq62uiesxxeyxoobmus2m", "3kzfc4iynszhil05q0acjgt4m", "pzl4dsl6c77mo7bt2ow6itbjc", "31af2cgs4rl4dgjdxxruhbwsnaze", "llxdkhw5c7b9i384f9mvig7o0", "0h2brcve4yaz6le5pyolkl5yf", "316awh4dg3fi7gjhxhp4mptp7wqy", "31pnddhti7mpsv6drty5msaypq4a", "445b38m2srygwmtiab287l6ax", "7p7msltsvktcjj5z373yim8p6", "rlcsxp1dfk4kzycunzf0d575x", "31o6gn3nzwlp3kovw2n7czgrmiie", "314373engmw2aoqn42bopuoruzgm", "312ainemt5kkcoo2lm5d7yus4phe", "312tnpnfcfbcplwa6flc6j2vatd4", "31q2qyvidtymrkhmxnkf6cxujbke", "31zo42hg7xwu42hxnazidtbhyu4m", "8ttis36cman9387qv5xg8whjs", "217pnmdkvn4ae7ex5tkcwgkmq", "31um7k6tkdznxazoe2jler45ilpm", "31vyeu5p6zv2t2aevc6hu6okngue", "k2xhhsexhrqo1opm4de73wgt7", "31cgjhzpnmfznbemrefhhvfh2vom", "nazl4", "314co727rwqnr2oommf772faefn4", "31bjg4ujqhdatydzkzohxyee6x3e", "31krnbnpktii3spf3wlcktfwe6c4", "31m3ts3wy4mhx6j52mix5kqftfju", "31exn7zkatydj6gcs2wxyvmnb4ua", "31o5oedf3xs2coxkf2wqcjdzompq", "31cp524xwykmxya54kd3vhkh5v6e", "31fxb2eaqatqc5breur47bjtjbi4", "314h4fmps5ncgx6vx5kuy2736uka", "5yowdwe9i2vgzco68e23n76p3", "keqxpluki70vt4ruktn80x33f", "312tsctxv6bvtm3i4xfak7o3gopa", "31ga5i25baoiweb3pdeedhpmem7a", "31pqeorecxh55iqxvs5puuifrr6m", "31s66wpewjaipkbgkjlkcwkw5j6m", "6rl4oiocv9a5b9ri6zzpu0bib", "046420nh4ftmspbh3fgr26tve", "z255f15mvknq0dpv0dh6chh26", "31mo2oq2j77kz77nqbqueauwalzi", "98e7ozr548cz06e3hlgs31n5l", "31wpsmgpakfdi4y2jkvwlkn5db4y", "3v64lrg03ejhj51hv344wftdh", "31lkqgjjwk6j7szrkygin2jre6tm", "ccd2p250a1geqr8lbvmi78odz", "31coe6wchpsj3fb3ufywtbb33viy", "i9erduboczjg27eclaanc8k2u", "31avwb4cce5o3dbids5oikyvp5x4", "31agz664gvkbxmom7f5277mvhpdu", "31yr4vfrikreohkfwg7hi7xrqafa", "316nyqlo2tcify5oddiqgdkpmx4m", "31yyknecxvo4cntljegyf3dhjw6a", "31zyma3wvbf2u7zaq7t3wkgkfgru", "byeo7xnmbiw4f01kdiyknxy9b", "kmkas4p2o0qxinfvdbc4h6l24", "31573frplchxodsp4hl5jiofyxyu", "im0mc1c5iuej4zndub5jugvve", "drrbqbyyl62anidx85mtjat20", "31v4bv24y4cf6pwb7yygobiaa3da", "31abjcvpt5ejf62hfh43azfmkhaq", "31e4k55sbybzgkq3qxlc5ltesy6i", "4i4ec3lb89mhmje7zsj9yvegs", "31xi5w75h6mxe7uv7iffh45q7pqi", "314kjken5b4qvvsgdvuxichkcwhy", "31ymm2crwfk3icmmeoyw3ulmlxue", "u32s6l3n3vmrlm31eqh888kjt", "21pvvceorsuxvoa3ogn35nvey", "oiimxrye9ue9qa43g7kmef0x0", "86bfhkmosztfevvkahfp56f2o", "31mhpxghjva2pmmtcptgxphvedfe", "8vdpitnwplzig0h1h73r5ids1", "0fjfu2jdhuljjxzp0knkd2mc9", "cwzltmhpo7p1ny35ik8rtkwyw", "xdvy6i4igh8258jvlqv36pumr", "31noyz7bqvmd6d6acguyievqox6i", "ru0aljgcd0ikb4b9bu2n6ozui", "31l6iuudmbpqnkxqsiuj3gowzqmu", "heo7nfg1prqej5t502x050gnw", "3127lrpwep234gec6hg7i47qigmm", "skwb7v0ykos7sawk2jbxhsnsx", "d16ssaarmoy8dy9mkc5r2hu5k", "yrtzg3s30zikduazl20mykvzw", "31zqhhfcf3i7dvpvoijnr7c25kia", "317yczxgshsmqiauradvczkjbnh4", "ebxo0jhtausz1hl77pzppybzl", "97gji086g81f2fs2o5x7jzc36", "9qo2jd888xx6g6oh836xdjbzc", "31bqh3qagg3rlkyagdk4cc4gffvy", "31s7hrgzj7eiwajs3brehorarb4u", "kc4ny34potz83ovru1iyav0wn", "mpio6xbyog0obad2sf0qcoddg", "31ovvn7jii5exit2ogh3dnnk2goy", "i4lrr3kfqr46yyck0jwnmymo7", "31jjz6swcbxm2orakxfabewyci6i", "qo8raoe7fvn67fdhvtsg7rui6", "31h55n5bgydetuad5myd6wvedit4", "31sfhq6lzdqkq4u7klzjm3jjkj5a", "b41r0w6e4p5bmpcrap5ax7e5x", "derickjoshua", "316epl6rw3ro34x3kcypipvs75la", "31zbjzyv6qgpng6yqbq3t7uwbdju", "317qd4ds3nby4nxw27e5qfzm33a4", "31ajm6lbpwo2d6emlazfegswmcli", "31wamtxo54dei5bipdox6ucapnbm", "7dmk731ndpctpe944rla7yixs", "31obxnxwyqouibm4nxpfou53tssa", "317rey6o6ltyrii37lmk5xy4bjwq", "tfrjqtlkcven9cyzob72619a3", "31tcmi6ou7uhstp3oenwy3ktog6e", "31fr5sq2dc57xjsb2qjqxysrlhju", "31opwiuncytczcgixnr5sncbcqn4", "31r5az7gepjzc4obqrzmslebhy6q", "xurrlp5hm769s2t2o2erbccnt", "31mdui4el3aslnmkxvidjbc5rxxq", "31nn7rk2u3duvxru5bwjcvvzgsha", "31h7fyhs2yzuty6dqkwe3mfjuwqi", "31rcb2lmviv6zwijkyhczj25ftpu", "31dxzgxthgrtjvxp3znpgkw7zpnm", "saraha724", "7sqvjtjcj9bvbm7uoxnbkxbtu", "0ciqo4whztzut99t57cbs3web", "6m4l6g28eymbup6dhzk5v3y4f", "31iagopowwf6cjfluhde2uv6ptay", "31s3jiykttdjbkazhzrxit65b6fu", "31a236jzywk7e24d3nkdjcysdxtu", "50sxxzwbxkwptebhtoa6dbxqb", "313mydnnuyhtj4kbqitxuwx57dge", "9okyrnhjj3j0c2gwfx2akf2ew", "zp8yfqga0b006euq3ttwp0qor", "31vgv3jcmmuefreshejd2andwqtq", "31u6zl54z7vyl3vpxrzrwzzrx2su", "31jb7bmwk2o263qr2fy5e6fbdgde", "31ap7vwwfubaert6jnq3oegoyccu", "3144umblkplmnbjolqs3mscztnqy", "31ayyneqiah7itrboat5kunhsrxe", "31qcuo2szpncb5ssupogtb34u6oy", "31gjo62hoo6afrgi3zrbbwtxu7z4", "zmbx7qqx7vtf2jrln434trg3o", "31z36levqjsqb4sh7yznsckantem", "31obslugwiip2dlirietch55gkxm", "dlfjasou86ou820rqwuv48g9j", "317t5zzd37ui7b6xetvg5kvr2wea", "31y7ptlb73mhzdipqub272atyb2a", "31urzog4h4s3zw2q6fb5lhb4z37i", "31tzjomv5wjfkwrbxu6ordznys2e", "31u76iybk4yig3urc7frneljr7ji", "31lmsgdzodkg2kr55cjmutkayvqe", "31mnd4lhkbuam6uhloi6vi2a6ave", "31b24prtvyklukaqjojxjhdvqx34", "313xiastkohw5ezhrddphxdoc2pm", "31tfzirejou3njmljxueyf7ttkqm", "31ngheqqya6delyjqabhivl4x4pa", "x5un65a3nt9wai8o0f35jbyhx", "31wbxdcucqxo4vopr576mpwfunfq", "co77u1wocy1p8k46qh3exdz6h", "d6d3xa8lsvnb4rfxzg2tptaj3", "31e2jkbqqeqon6mfdwrl6wewbrum", "31j3dlfmrrhj45nya3jl6abfphnm", "31y5s6avtxunbnyemiczr5bevhte", "317a2whahl7dj24atatri4m6gs3y", "r3ewjmygfvmj4591kc8wig4bb", "jcuhmxl4qemhb11nu68i0w1rp", "57tkayniih1x33wga8xr5xwlz", "315wlt4xix5gpl52jrii3y6nsula", "31ltwthk27qfacgwldvj7nmmrzxu", "krw1d0e28ywypi6mwnojnauva", "ldxi3uldm5kj0ts7qoeuh243w", "31wrq5nzyv2kneeixhnlosyozoym", "71tfw3plgk8v2x3ftkvxk7768", "cy11d528eiiw0dy6tci1diacf", "31mzhtemzrqnpeb7pydytakiilsm", "31xfzvroruvfimkxkv4zpkge7hgy", "31ayp4zdedwzm6ps5yunibvc5ori", "31bqolldt65u4inewd3j5zvjyppm", "f49j38tn1t99o7hmenm9qxwrw", "9yvdo4s8nwv2zfjx3r43odhei", "31ed6lola6uxl4iwce2fvki67a4u", "31qz7ufmlzyp7gudjaqvxfhul264", "31gcoxw2si5lz3j5ums6skuie3vq", "313hsp5xg3gzcvw3pt24zjqbcpiq", "db44hkhq5kud5dsvgj90j29t1", "anaskachandra", "314fa5jeyzeze2gu2ezllvjn44ii", "nqkth3g0tg7lmr76ow2588de0", "gjr700gi5ds7o0ocjd5ng75dk", "31xcouy2j7pk4rje2pqelfw2weiy", "31tc7xavagz4xprffgmq2d76bc3i", "dok2b9xrivykia74j5x9qylv6", "31xw5djoifgg5vxcnmyiimahcxiu", "kqyfyd7wq1mdjy7323xywf2kj", "316zok6eo6okqpddzyljnrhuf22y", "31syuhksicuw2mlu6wjks325ivs4", "wkgpklizwfwwb1iff3g9809zz", "21pmy5mvms2nbvaa22wnuzkqa", "31qyusyeukndu5dvr455foe2eo24", "6fl6689lzs4md2omkw4kvivs4", "2bls7i37114ertz7599dj055u", "215hm5yqkevlngopmjwky5gpy", "31wsvxsly4keehfinaxgox3qtl7a", "qn26aofe90m6dim4vz28bgbo8", "315pz2xubqwzogcgiew3xax74ug4", "31j2nu3u44kwrpgdirqjapn3jwzu", "znimozwyib0tdjnjcdwufq3o8", "31liuooi3rnoobn46pb6uda7v7ny", "31ccsqff6tsudhnpswetlh2cj7cm", "312hahrcczi3a5j7cae6z7zg6a74", "31fvuws37xpi6vhosbpf2zmsobz4", "98enyo5twrupsyf524lywkusw", "31cxgehazznr7mhobwkobqp3qyo4", "31y6actkuzzxk3acwcbyq2mt54pi"]
try:
    for username in usernames:
        playlist_ids = fetch_user_playlists(username)
        for playlist_id in playlist_ids:
            process_playlist(playlist_id)
finally:
    conn.close()
