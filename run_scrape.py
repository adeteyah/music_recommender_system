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
DELAY_TIME = float(config['api']['delay_time'])

user_ids = ["31oxwxzfubwtz6kccd35z4bodxeu", "31f7dowblu65o5tm2ytlihfpmcja", "retrop246", "31d2wv6nbivzasqd4yhnpich654y", "31ldjggq7dffc5fd7b5v5gykngum", "31oibq3eip6mzbyxsvkahednyhsm", "v9eyndmar5dclqs2fi32p50x3", "31boftbonqv75o5qyxylpi5y4iue", "4htkrnw2lmftp8eh8rsmyiz0w", "3yrmad20f43u3tsdso5y1v8hp", "31iddudpyapmpgttadfimg5uudqi", "uhcxuymhrqgpb7ssntxq1vn2l", "50sxxzwbxkwptebhtoa6dbxqb", "31nn7rk2u3duvxru5bwjcvvzgsha", "9q2rheweu4guy193272tsdlym", "21gsrc35oj5sfyvq2zkfqjsfa", "31go7vwfb5ck75ff3dody7e3qoha", "215hm5yqkevlngopmjwky5gpy", "31uileq5qbtgcikphrbe5ucxo6eq", "7quc8v24qvzkf14qfxw0jpapb", "eff4c7i09cr6wpfsrkkjeo1xn", "31rtitfiqnf34pbeeemqr7pxr2hq", "needforspeed", "e39ooyk86712qwonvpt1hioeg", "j2r2nz9pxskup6zysxyg1jgk4", "31fbrhaphhakybvsrbzjzvutxc6m", "31mv5te6hwhf7zifi3etqg27x4lq", "31skwvyfklznwakrtqwjnzymoizy", "31prgg2i67ig7pvndbxtmwc4ftay", "31nbr65t3p4edyow3lgqrqzapdja", "31nha23rnp5vja4qidpkxi2ne3qe", "31untxr3ywx5wim3u3nec5f46wza", "31ebzeurveo4drqgu2cumifrfruq", "31i7b27dyeqallz3jnj5alwifoda", "31gkuqgiau5fc3b7rcqwezhojocm", "31fbec4xv6qv67mt7asl7cnwze7a", "31qz4jxsq6ekk44w3rftopjexgji", "31nk7k7vjmmuakblhsvjvcrjq35u", "31gajedep6ol37cogfh45fizfcai", "4ueru446vwbv0xpootfd0abda", "31f6wrkqnl75ubznffymg72m7uui", "31ksspesewu5ezrnc54szjwktu3y", "31zyma3wvbf2u7zaq7t3wkgkfgru", "rcelnre67j4rg795pjd0oj1bx", "31ohefa5xa32sd3izskkovsfb52i", "31famvvjqzsnaoivyroqtro3cwc4", "31mwpfktd2pavwsuh6pvpw4anfum", "zsaymizci7yi7s5wqjf73qng5", "31jbatpo7pwzsrznywy3gtjtayoa", "3147xhyrmj6utnsn4aqrjv4qjsle", "31tucvl2ejkbyt6tj4slaf4v3i4e", "31fppanhx3oh6rslrm5yiy343ohy", "rw3qaxpge0j683vi61bht9tlx", "31bzayzzfxikinuvp23gqdytj3bq", "609o4zm58xtcrobfh57rh68k9", "31vzjlftil5sxtfnmnvmuie65vke", "galuhm", "tcpwhovu7b961jxkt0fa665sp", "31zrch6u5dqqnp6lasvfnh3nkhs4", "31ioocbgmzfpverohcnx5xkschaa", "y69rrmpnezifghulidp30drv5", "s7k8oamnr3w5g2rr6a98vh6yx", "ihx97gl9mpsj3wmmx5os2dkoc", "firatkaya90", "31cdyxs47bj3kpo3mlorhjb23epa", "sc34mio3ssd1uvbrfvpi6pkk8", "31dzbmz7qjnea3ebvee6ww6ezqo4", "31codzylmxjlfcyyeapgk6d2zqv4", "nfdrk7zus15hxca4byjxvssqk", "ejm3owujrjfa5b2p4b6ag6hq3", "31b24prtvyklukaqjojxjhdvqx34", "31gpn4hyghgppcseel4miw7bkevy", "31nhq4wd3epgw6vpfeb5ewk2ekmq", "31mqrbjfo5h4r6dqnzqqe7fl356u", "31exco6c4ffon3evy2brzdrf4ica", "31tzjomv5wjfkwrbxu6ordznys2e", "lxar6q2s7lzyu17yb2bbkujq6", "3137dhyveewl6kz5s6qstnvn27py", "y008bk8i54q9fpcy72h4mslsi", "3o2b9znh8mvti0tygl34dm9vj", "uf4uvh2xh73uvnv0ebvtmak6e", "3lde8252nxvll8217wvw38vr5", "31cxgehazznr7mhobwkobqp3qyo4", "n4mbh3s243gjb5dwenngdmmr9", "317bs72djo35f3a23xgjewtzzuam", "3164a5jdwjcw7ibdbordbjybdyt4", "31kt6icnabnwfydzmfuhittnwum4", "31malh3gpcdn37d4stxz2nntpd2y", "31sq72fy632mtdxmpan6ctjtdsgq", "31iencsxzwxmtorukemd7naiuu6m", "anaskachandra", "31erhzhlgk5z5ekz6qxrf3zk2m4u", "31uzxsoyqzjiu4mwx4fjsjrv2dym", "m64wdycqz3v5w0tpxxvnp7iqq", "315565s3cobyuqzf7yv2jxgcxbyy", "21llwb2xam4hq5zdpnw4pki3y", "31g2xcafdltxn5qtxvnzag24gm7y", "31amca6vjtafuxzvajp2hedutdbm", "5gn2980f8huyl1k2h3gx5ep8g", "vhemn7bz69e9298j3cul73ujs", "31kr4n4lw4gjvixiy6jtawbceg6u", "2ijgjaelqlcn09aq9t7bfn09m", "31gjo62hoo6afrgi3zrbbwtxu7z4", "31tjoxe76t6rjn4h4t7sje4r3tya", "31uwmqmydmuzrmi2z55vb43rm6tu", "7p7msltsvktcjj5z373yim8p6", "dlil61eki8svtxyu28b5xl7l2", "hv71kzwc6bkesppim6jte9ep7", "k7nb2ou6s35b8n7iuaezwzj67", "31epdtztvallfce2xwuzyj5sacwy",
            "31qhg6rr5ocwcvtfxqmh6e7vrcim", "31x3r5qlhy4tivtfyqhpwhfcdyva", "98enyo5twrupsyf524lywkusw", "31ivk2u6zu2ud6iqudxwzfbal7yq", "31kyuz3mggyuzp3as52fqdnswate", "31obxnxwyqouibm4nxpfou53tssa", "31mfxs77xqovxm2vhqgd3ttpxr24", "31epzxvv3yihjl3y4ytaodgu6ncy", "31odybzaej4le37jxjokk5k4ajse", "31vyqksy3lglbqappqroxwbwn6ne", "31atx7o3fk5a3u6mqdqhax7hjw54", "31tcs7ijallucv5xijjjqr6ldwpi", "312i5jp6cvhme3gqltehs6mxtloq", "derickjoshua", "o3gbpul098333bu75sj2m9nlm", "31ewfsazwim7gak7intvm62v6tqm", "31ihy72rlvhrpagdrowncty3bq5u", "312pnpr426x6qckogofjz5yznzwe", "zmeaa9mk2aunsunvtrkhn202l", "f49j38tn1t99o7hmenm9qxwrw", "314ilajwouji467rrgtyqr67lqyi", "06khqj41bk3ghe55gefpqbgc7", "3146oo3tla3ogoro5cvsxipodg24", "cz9wd309f3ieleibpracs31wd", "314vj3wnsjfh3eldvb34iezpxg6a", "vontg4rrmyrmzp5f59zou6cnq", "31qeks2rj3auclfyfqxtazgftgi4", "am80p57hiz2un1zfzs75va8wa", "31va5imumgul374e4cc325iwehsm", "vy54g0xyuu7r5x9wjw154zorr", "31xbug3marbce44smqsh2qok25my", "71tfw3plgk8v2x3ftkvxk7768", "fctwtjhwluss52dh3zu25a5lg", "316y2a33nwhegp2e6v6o2wkj2uwy", "31h5f3g3525wktpr3klrlz7okeiu", "ivena", "timeout", "21ofvvkw6dr52jjcpucv3fgna", "wb09hvocyvva4rmrga98d5ql5", "31cdwcymmj6q4qyfq5e4zgw7eb7u", "31zyqvckn5sxvwvcwv546bxgqs4e", "9y3pgwg89qz14ucchfwk7l0va", "31uvelyy36qi7vrkjt53stbtmzhy", "31au6afj4ohqrw6xnygszar5m2ey", "31l5txw6x7y3f6jmoxkxzfnux2py", "srluvymjplbpkrg1a17wsy9dn", "po07ba3xzoev01btodj8d6ww2", "313b5izukwew4lm2qilryym7vwvu", "31up6dac44z6alrfhk3sg2avvknq", "gnyfn9kgg1i44drccf4hy5urd", "wh1rv9pjueqn7iybla1mf365w", "67mmxu4j95ggjky4xbxd5w7bt", "31mo2oq2j77kz77nqbqueauwalzi", "31hmbz2fp5yllxeoladvl5o4ku2y", "31i44joqoctd76p6yp253jmxx76i", "31vawrvumuktinymgkdclj6l6c6y", "31ke45sv7lg3sn4oc7pslblkuhru", "31xvb5dwguujxeuld2nbyr6cq3cu", "rgkn6rysyg1pm3blydjw2qrjm", "31hyfi5cvdvr4lkg3wwmqb2k7any", "316lqgdv3seif6pi2kxncnnoylfm", "31cg3t6fwbdzeenc7kp2vlkiacsq", "d0dayhvjf753h1smgvhy758mo", "31mr5n2kctqgtsbyuuf2pxgn2fwe", "315h3s4cbtmtqnf7plvxhgs2pope", "31e4k55sbybzgkq3qxlc5ltesy6i", "31bjrtdqkaunrndkokiee77v75se", "31b7hl3y5dlsc7fgbxkjdsab3tn4", "31572dnwl6qwsaupakx2vxygiooa", "31ay2furjrc7lp7kzvgo4keuygsu", "31urupz5a6pfq4ejg6mmrf4ugevu", "31te2lgb5ejgwhztlbyuiyg27vam", "d6d3xa8lsvnb4rfxzg2tptaj3", "zs4ptmqj5su4799omo5doqqc5", "31fyublnu4cmibraewf3vffafdha", "31fthnoaskjxf5z6ylsxpjbhlw3i", "5thalr14j490nlk8kjaridu1h", "ujgsv4avs0dsq6eh6g486j9jo", "r0tmmvke3s0818p8dlrbkoref", "317w2uirm3napnv2sczkoqh2tes4", "313gz6d4dmexn4zybhdgfb5zh5eq", "og0qa76j35j7t1jggg7jfdr65", "31tecerevh3t3dv23a7ur4aj6nne", "6xa9jwjjf0wm5n47i7r74udzh", "31c4bbow4tkeqyb3aga6oxtv4gbq", "31pll7djmcx45arajnssgdjh55mq", "317qf4qpdmdnmi26gvvpeynwklae", "31gvg3ucujf4ol462uc6e4bg2sxq", "31xfzvroruvfimkxkv4zpkge7hgy", "31memxmxl6y5henpa3edulmh56eu", "316iqpoodpwo4tfbavuft2qt77ou", "c6sxilrd88i22c0ekpy165yn6", "316awh4dg3fi7gjhxhp4mptp7wqy", "vtdjajo5pfjh5i91nm7ohe70h", "31v2x3wrjc5kszqv56hqltcj5lae", "31diledb7c63b723psni4uznmxae", "pfrzut44ax304fv5ls03x24zj", "31fdyutkgekxvzghd3zlskpkjh3m", "31liuooi3rnoobn46pb6uda7v7ny", "31cgx46x5ro2joez3rkabfo3eot4", "3132b2t4h6rxbayw7udirgbpdyba", "31kuqmrp4y4qlc6unmahnfbmnyty", "31fxb2eaqatqc5breur47bjtjbi4", "313dqmc2q3elz2gxtl2phhmsxxay", "y5hzoh1tkcv3pbbsdz0uz7zld", "21uqz3utp7bjlw7botrdamsuy", "31ss5jxh3hgd4gztgqpbirhctfhe", "31k54pkgikmhu7ajbmkx2dp5zxpu"]

client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# SQLite database file paths
playlists_db_path = config['db']['playlists_db']
songs_db_path = config['db']['songs_db']


def create_connection(db_file):
    try:
        return sqlite3.connect(db_file)
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None


def fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs):
    try:
        offset = 0
        limit = 5
        fetched_playlist_ids = set()

        while True:
            playlists = sp.user_playlists(user_id, offset=offset, limit=limit)
            if not playlists['items']:
                break

            for playlist in playlists['items']:
                if playlist['public']:
                    playlist_id = playlist['id']
                    if playlist_id in fetched_playlist_ids:
                        continue

                    fetched_playlist_ids.add(playlist_id)

                    playlist_details = sp.playlist(playlist_id)
                    if playlist_details['tracks']['total'] <= 5:
                        print(f"Skipping playlist {
                              playlist_id}, not enough tracks.")
                        continue

                    # Store playlist details
                    cursor = conn_playlists.cursor()
                    cursor.execute('''
                        INSERT OR IGNORE INTO playlists (playlist_id, creator_id, original_track_count)
                        VALUES (?, ?, ?)
                    ''', (playlist_id, user_id, playlist_details['tracks']['total']))
                    conn_playlists.commit()

                    # Store playlist items
                    track_ids = [track['track']['id']
                                 for track in playlist_details['tracks']['items'][:24]]
                    playlist_items = ','.join(track_ids)
                    cursor.execute('''
                        INSERT OR REPLACE INTO items (playlist_id, playlist_items)
                        VALUES (?, ?)
                    ''', (playlist_id, playlist_items))
                    conn_playlists.commit()

                    # Fetch and store track and artist details
                    track_data = sp.tracks(track_ids)
                    audio_features_list = sp.audio_features(track_ids)

                    for track, audio_features in zip(track_data['tracks'], audio_features_list):
                        track_id = track['id']
                        track_name = track['name']
                        artist_ids = ",".join([artist['id']
                                              for artist in track['artists']])
                        duration_ms = track['duration_ms']
                        popularity = track['popularity']
                        acousticness = audio_features['acousticness']
                        danceability = audio_features['danceability']
                        energy = audio_features['energy']
                        instrumentalness = audio_features['instrumentalness']
                        key = audio_features['key']
                        liveness = audio_features['liveness']
                        loudness = audio_features['loudness']
                        mode = audio_features['mode']
                        speechiness = audio_features['speechiness']
                        tempo = audio_features['tempo']
                        time_signature = audio_features['time_signature']
                        valence = audio_features['valence']

                        # Store track details
                        cursor = conn_songs.cursor()
                        cursor.execute('''
                            INSERT OR IGNORE INTO tracks (track_id, track_name, artist_ids, duration_ms, popularity, 
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, 
                            speechiness, tempo, time_signature, valence) 
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            track_id, track_name, artist_ids, duration_ms, popularity,
                            acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode,
                            speechiness, tempo, time_signature, valence
                        ))

                        # Store artist details
                        for artist in track['artists']:
                            artist_id = artist['id']
                            artist_info = sp.artist(artist_id)
                            artist_name = artist_info['name']
                            artist_genres = ",".join(artist_info['genres'])

                            cursor.execute('''
                                INSERT OR IGNORE INTO artists (artist_id, artist_name, artist_genres) 
                                VALUES (?, ?, ?)
                            ''', (artist_id, artist_name, artist_genres))
                            print(f'Updated artist name, genres for {
                                  artist_id}: {artist_name}, {artist_genres}')

                        conn_songs.commit()

                    print(f"Saved playlist details for {playlist_id}")
                    time.sleep(DELAY_TIME)

            offset += limit

    except SpotifyException as e:
        if e.http_status == 429:
            print(f"Rate limit exceeded for user: {user_id}")
        else:
            print(f"Spotify error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    fetched_users_file = config['file']['fetched_users']
    fetched_users = set()

    try:
        with open(fetched_users_file, 'r') as f:
            fetched_users.update(f.read().splitlines())
    except FileNotFoundError:
        pass

    conn_playlists = create_connection(playlists_db_path)
    conn_songs = create_connection(songs_db_path)

    if conn_playlists is None or conn_songs is None:
        print("Error! Cannot create the database connections.")
        return

    for user_id in user_ids:
        if user_id in fetched_users:
            print(f"Skipping {user_id}, already fetched.")
            continue

        fetch_and_store_playlist_data(user_id, conn_playlists, conn_songs)
        fetched_users.add(user_id)

    with open(fetched_users_file, 'w') as f:
        for user_id in fetched_users:
            f.write(user_id + '\n')

    conn_playlists.close()
    conn_songs.close()

    print("Playlist scraping completed.")


if __name__ == "__main__":
    main()
