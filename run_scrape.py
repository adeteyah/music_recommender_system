import time
import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.exceptions import SpotifyException

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

SPOTIPY_CLIENT_ID = config['spotify']['client_id']
SPOTIPY_CLIENT_SECRET = config['spotify']['client_secret']

user_ids = ['mfahmihdyt', '5kiix74ac3smhdwhd3rot5trq', 'r1mwtxwamwam6y3wngtlpbp8f', '31zrjhao6y2bchstgqzuvlj6gxru', '31eux5j4xfx45bpenuabhwm7ig64', '315yinp5n6muslkat2ertawswlsa', 'mav946uiwcow86or660mp3xk5', 'e20w0n5qg1jlp0x400oy5w89v', 'ufnooj8rw6femcbkbuzyn4cbd', '21pqwmpmcutzemesmqlx2nibi', 'x5eijockr7nni1ul6voobw25w', 'alencdds', 'lqsgdj8cbtsieuuneyx6dqpl1', '31a7243toh5tgcgzr74xrthdoe5q', '11iuk5uvfcupr3y347ptii20a', 'aderizkyputri', '21vxtd4uv2wte6r64r476ccyq', 'cmgjyapu6niye85lasaht8acq', 'edgardomenic', '21pwax2j6lg7c7nf3lu5bi7ga', 'rmwqd50o99rmd6thg8zd99w9q',
            '31m66xdbx5u3ct5dhydhrakjfimi', 'thelorgorenk', '313jkbzmyb2sbpvq55c6pvl67lcm', 'az10shokjxa5lnbg2iuymr7yt', '21ofvvkw6dr52jjcpucv3fgna', '04sza9infee7w11b213snaek3', '31kqdaxzao3ik62c25v3gdpivpae', '9agwjftrhb05vrpgkykb5jd4h', 'diatyo', '01f3ueieht1cs6l3azpll97v4', 'u12mt9hqrpl8suxpuoahb5agv', '31ho4muai7tzdertxq76nfri3ab4', 'khatamiy', '21o6lrhhvcawki7hwp4b6jpeq', '8nipm520gxvxon8ze0s3zblgi', 'qjvwdfnldn27ro7713yxb00pb', '21x53g3wuugdyfrcbyjf7jtyqhttps', '21buf45wkhxocbtmqospmilfa', '31bwpmybiyutryd3l3rug4lbvvxu', '4xr9iteppqf6b8d3w0u3mrdwt']

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn


def save_playlist_to_database(user_id, playlist_id, conn):
    try:
        playlist = sp.playlist(playlist_id)

        if playlist['tracks']['total'] <= 5:
            print(f"Skipping playlist {playlist_id}, not enough tracks.")
            return

        cursor = conn.cursor()
        cursor.execute('''INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
                          VALUES (?, ?, ?)''',
                       (playlist_id, user_id, playlist['tracks']['total']))
        conn.commit()

        tracks = playlist['tracks']['items'][:66]
        playlist_items = ','.join([track['track']['id'] for track in tracks])

        cursor.execute('''INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                          VALUES (?, ?)''',
                       (playlist_id, playlist_items))
        conn.commit()

        insert_track_ids_into_tracks(tracks)
        insert_artist_ids_into_artists(tracks)

        print(f"Saved playlist details for {playlist_id}")
        time.sleep(float(config['api']['delay_time']))

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded. Last processed playlist: {
                  playlist_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def insert_track_ids_into_tracks(tracks):
    conn = create_connection(songs_db_path)
    cursor = conn.cursor()

    for track_item in tracks:
        track_id = track_item['track']['id']
        cursor.execute(
            "INSERT OR IGNORE INTO tracks (track_id) VALUES (?)", (track_id,))

    conn.commit()
    conn.close()


def insert_artist_ids_into_artists(tracks):
    conn = create_connection(songs_db_path)
    cursor = conn.cursor()

    for track_item in tracks:
        artists = track_item['track']['artists']
        for artist in artists:
            artist_id = artist['id']
            cursor.execute(
                "INSERT OR IGNORE INTO artists (artist_id) VALUES (?)", (artist_id,))

    conn.commit()
    conn.close()


fetched_users_file = config['file']['fetched_users']
try:
    with open(fetched_users_file, 'r') as f:
        fetched_users = set(f.read().splitlines())
except FileNotFoundError:
    fetched_users = set()

for user_id in user_ids:
    if user_id in fetched_users:
        print(f"Skipping {user_id}, already fetched.")
        continue

    conn = create_connection(playlists_db_path)
    if conn is not None:
        try:
            offset = 0
            limit = 50  # Spotify API maximum limit per request is 50
            while True:
                playlists = sp.user_playlists(
                    user_id, offset=offset, limit=limit)
                if not playlists['items']:
                    break

                for playlist in playlists['items']:
                    if playlist['public']:
                        playlist_id = playlist['id']
                        save_playlist_to_database(user_id, playlist_id, conn)

                offset += limit  # Move to the next batch of playlists

            fetched_users.add(user_id)

        except SpotifyException as e:
            if e.http_status == 429:
                print(f"Rate limit exceeded. Last processed user: {user_id}")
            else:
                print(f"Spotify error: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")

        conn.close()
    else:
        print("Error! Cannot create the database connection.")

with open(fetched_users_file, 'w') as f:
    for user_id in fetched_users:
        f.write(user_id + '\n')

print("Scrape completed.")
