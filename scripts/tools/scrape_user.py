import sqlite3
import configparser
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load configuration


def load_config(config_file='config.cfg'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


config = load_config()
DB = config['rs']['db_path']
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']
DELAY_TIME = float(config['scrape']['delay_time'])

# Replace with actual user IDs
user_ids = ["31swdsv52kgvgq7nq3e5tviysgwa", "31dri2c54aoop23rngnxjhum3neu", "92v567ug642bx5l82xp7fk1re", "cz90ghirbz7mgru869di227f6", "31f76k6llm7h5nisfkltbie2ejxy", "313qmv3s7nrmjwesnxm4o6yltx4y", "3134aom2hx34wqzbpd7u4gthdjha", "312tbhsvrq5vlssk5cmznltm2oba", "31hevdqfr3ustu2tmcpxm7j4ialu", "31xmgou7yho4pc4ieqlemzlo6ooq", "3yvocu3jsaq8tmjulsi1tpi76", "31zfzjx2s36q445aexnrrz7ttiny", "31r5x5l52wbems746gjk3trlbj3q", "kiksiqvvhlqpeswfcjwensmnt", "euwlurl49kpypddqcbj9yak5n", "31qpm2zyqubrmadw4pscjlgdcct4", "31fppanhx3oh6rslrm5yiy343ohy", "secpzb1qeg9yhz180ul2hur3z", "f0pyg7ud68oe21dpzr883voeu", "31u3u7gf36fgsenfxukxyihrjl7a", "etjd8apuacgtvw4afdmh7z792", "vm46cis8wyijpi4swyxguyml2", "wncaxmbwrykqq5pxqmga4ldfh", "pn2vesv93a5q269r34lccpkez", "31z4fb35wl3toewiwgwtzdh3i7v4", "e4j6ja4v7oxwm0xs90yha69gl", "9pxubeg6ekdunumzum09zpiza", "31zzt7gic7zkxnphqmvytdru7nwq", "312zhsbfqmazltsifjhlbukypaki", "314jnt7wgtsrgvcjdu4kyv2ihvx4", "31tcs7ijallucv5xijjjqr6ldwpi", "31a2b7hoayjunozzcv3aqg2eerx4", "31e23kw2vmpehtwe3f2dmrhwix3y", "31okooa246rf7ydhlt3nrhdzyrc4", "31zp6bexpieoyu2osdp4dsvoppqi", "31mgnh4w2xwz2jdcrbodwd7pwlsu", "ihseeyu5daa0l661x9nrr08w6", "31hzix5rykijvmfz5ait2vjjdcye", "xx3mu6gcjq4h92kry0lxjoczd", "317xmmo3f5aiwr7mmwhl2j45zh5q", "13xrrza3fw8k5j2terdqc0ou3", "7n639iyapqddsq6frg581wbt1", "suryakencana7766", "314uico23ihchcoi6maj6glwxbla", "31fsiuam57dg6njq427cpwllanxu", "31lwzxfazffskhg3jw5o746qayhu", "31go7vwfb5ck75ff3dody7e3qoha", "31cuxlxmof5r45xq3kxx6odb72qq", "3133tft6dmev5iyhwjrljgdamria", "316oaajjr7gai4eqr3gh7ytlciwe", "31kuy5z43xbrt7iu7xmrundhuf2m", "31nv46zp32ruqmudi7co7evu7rxa", "31mv7xf4tht73obvycszn3gkbbia", "31aqrkionnucuwoetwo4oviu4v2i", "tcpwhovu7b961jxkt0fa665sp", "31fyublnu4cmibraewf3vffafdha", "3o2b9znh8mvti0tygl34dm9vj", "31aod36bqoojsx2u3khl5vylrdjy", "31haxjs6o3ka3ha7vbppg4txsxk4", "0cqdaex19z50p9ovn87hgvtdj", "5fmzxnv74yzefzlajyswgu5vm", "li13h7m5pyhtvtm2k47l4k4a9", "316root7ttunxvl574felxrtthey", "jakenov123", "31gbvhmxfwhb6hxjo2ygnukzyv3q", "dinanari", "31q4qwyobanoiugwndkpmllgmqvy", "3122cztm54ks4qfibzcrt7vojbui", "31g3e3fhhdketsd5x5oitos2tyou", "k23d6pg0j6dgd7e1hljq2a3aa", "31447dm2whdehswk7voqkudniv2e", "fpgwa2z8eg7uzbuk3mbfs49n7", "4ol2bf7a3lbydxx6uyhp39np2", "ydsrmlxv6z3ztqfth4zwjy4bw", "yrgktf8clvcas2et2za3fdftx", "31atx7o3fk5a3u6mqdqhax7hjw54", "jplkkqun2b29w5fs1n8r0xfcq", "31oitedxssor7sl2e2ifpo62r24u", "y008bk8i54q9fpcy72h4mslsi", "icso3d7tem82lk0mzpftgjcue", "31dsithof6yeyibdz25i56rezcpq", "31xcinadgppeixl2mmq2qwtxdqsy", "31g2xcafdltxn5qtxvnzag24gm7y", "31lc44fmoiihv3hd55rehonlrblm", "31vy2mphx57fdg2c4y7ks5n7s3v4", "qckheaowan0ou4afuc94nfx1g", "31kc65upc3ravjg56nzgn5k4tgke", "5gn2980f8huyl1k2h3gx5ep8g", "312hj6ply4zx6chk7n3dbsu2okdu", "316ahn4h4j6a2aidoelkuwslj7cu", "31yeofrdlw453gyxooahuvv7ke6e", "31ajr35dbvgqtjy7jvfkbb7rpqg4", "315d6hx66y4etzbwmomsmo7evvpa", "31ujg5nl3rjqrcn2kyeyfd4nhrxq", "31hhu6bgi5i62vugbbzjbtsbcdke", "v597bx3rdimunu7xnje8ox0qn", "31bvrupvlnlnbhdcahte6nzbvskq", "31dstiviepefsqbwdk23w5n6iiku", "31qs7dg7jjyg2ja5oe3kpl4g3one", "31fdyutkgekxvzghd3zlskpkjh3m", "31maubxg6iq5xcpvsicjczbb3upy", "31ikddha5pdneg463qnf5ilhs7dm", "31vwrt43chr26qpgg6g2zysjitfu", "31uvelyy36qi7vrkjt53stbtmzhy", "31uaj33sg5u2bwnfcnsct5nmkkni", "jhx1fo9whzmdm9fmkzwvhad8u", "31knrkesbmdjpr5dey5vctbzlcku", "31ksspesewu5ezrnc54szjwktu3y",
            "31legej7xjngmx3klyzaq5ix4dam", "azyphgt9plsjiw61mlgymcufm", "31x2wknipl53b6nipp2pk3k7kedm", "31knxj7mgxweegbfkumspcpvw3ke", "31icwiuvzjvxmkztc4mc4lfek5ei", "gd3k597409ilqw2yukrpfey2p", "6ec6kh5fq9b41m3g1wzurk70u", "31ziasslio6xzsggtdvdl3grr6be", "y18yq74p3ecbdrkv9v0vvj940", "315hnua3wyrvcmnjzeffx4wl4q4y", "31eleoztptmst4arn7yzdfbeqliy", "pandji", "31mjllsa4msrmj7ke554bvc7qapa", "31ufly4srxscvaggnxa2mnv5hfca", "31652lbut5z54v2d7fip5m275cv4", "31wglftx2snlrabr4wnlozn3a6ce", "r0tmmvke3s0818p8dlrbkoref", "31sgebu2j5faspjds4bbuhke5qca", "316vddyzaczmdu4ajrtdw4uxaa3e", "31aabywfguwaabhtkb7gi3gnfs2a", "31j434dx7qyma5lwg46ba3nj62k4", "31qzpnqpd5pysaodof7ghhc7ucwu", "21jggsa7iaex3vedj6iyummdq", "31muhxyl3avkifbyim5m2zisy3ke", "31gn7j67flpzzk4z4fv2t4q5igwm", "qet9coix85uvzi9mfagfifhj5", "cerbnir8cptj5bz9selat7hyo", "316che4452qfzblznggmzpad3dfq", "31vgwndvradjqqdthjqbseq4nnzi", "31yvh3h63xpr7qoq6pwpuice623y", "31z3f62fodmnovbrpzktsvhbhalq", "zgy2xoe966pej7obhkmsbogb3", "315w4ce6ycoluwlai7by77ptem4i", "uu8h6hy4t63y2bkubwtqfik29", "lsqr8q97ql53v5mhhhi84tppk", "y3lqvyx550pm2l0rdg0d47utg", "nashw4aqila", "31gkxeoyni43bhcixomjxjwflumm", "31n3zk257l7wfwrob36jjwzspvza", "adhqw2slhavypwaqr25vgbw2k", "q576kumoyez5qlvuz3ixnmelc", "t13ensa7dk6y2v4fs5wy3tmgn", "31ydmsb3tdi3hwwdpty22qzrteim", "31nk7k7vjmmuakblhsvjvcrjq35u", "4kdk6jt9dib862oyyt49re41a", "e39ooyk86712qwonvpt1hioeg", "31nz3qyqvy7cssaj2pzfqftbniwq", "316sef7itzp43usrtgjxnftaksay", "cu4kf76fw6czeaqh7kk7xp507", "31zvnigkidb2jbd62zvjear6sjda", "317azgvamvchoinljyvkpwn5sapy", "31cyhas7e3j4epynd4rhwvrfz2cm", "31n5cqxbb257uqlegsmzc3zcx64i", "315fflmmp34lkxatkhpc7nvfwiaq", "31ydtj44mursrzlxppepsbys7ttu", "31f3nfirfv2gxumoyk65qnhayl4y", "j9k7dvusxuegxvj3apglsqhrj", "31sk7zgqwdm66yk3ssqe56olwvku", "vjz5wwxrlzhbre06dzz7ok9qb", "31gytzwf57fv6j6j2bxdpuobrowu", "31pjheaqine6vhv7iehzzxysaff4", "31xlbmbaf4tnk6wvnqbnponpeaiq", "31uijvygql3vqqucfuld2autf66m", "ce0obfetwz33sbmobvxo7hlzc", "31ekzhwhkc354qhnle72qybdldfi", "31umrqgly5ucyiux5flluwdanhwu", "22wgatbxvyioedkokpfkh6gdy", "odydasa", "314jll2yhek2ipmxk3yzf3iogumy", "317t2ehkzgnjfy4xcankis4bkgry", "31mfbgeeo523qfbtqjs2hky5grkm", "31iesalccampel4ix5543ktwrqb4", "jx1l2l9qf8tuh12qifjgixjjz", "31n6i6ajjq3uw6ftunsoyybi3si4", "ru5jo939ejw3pai5kzjvegrls", "3dnevoqoqg2zfv6r4fgczy70l", "31h5r5lpjejue7m3nfdkbjxdehjm", "31mmfrkle2ka64ruttuxxixczv64", "59mvpg4e08yqp2gwr03ab82tp", "31mwpfktd2pavwsuh6pvpw4anfum", "31ohxff2uxjpfl4wihwxjjerhxb4", "31gzzbjpwtnjha2wqe6okrtetblm", "eu51vel92ow2vcl0uklo0rlae", "31fohczaxgze77meienv2uftpgte", "31hoipusgiz43hjiy3cv62scfbq4", "31vtyj6ilzejch5a62jqdm6h7rji", "31uu5qpcwt2tfrabddxzr5bpsq2y", "31gfvasn6eoiwmjmsy2ioskilh3a", "31wa32a7gg5uiwfhwdsstwt76kjy", "wtj64jfgksm7v6gvwomscarhw", "qk4rlt2q8p2mezw836olioal8", "31ywmgzmv7aggvupqdgsls6jezkq", "312z3e7mj7p7tjw7bwkawz4te6dq", "gurxzh05nwmzehrs9m6xqiaru", "xf6hs0hhh611vbk1scxxq1wxf", "3164a5jdwjcw7ibdbordbjybdyt4", "timeout", "31kthi4toakgiw6o6ygjqvirkx3e", "31lyj346e6ryt6qrynsukovozhgy", "31frzk4muhszex5zitsnhbgrmrae", "3122xjkrgku73yzeolzwvejnsyxq", "31momaetuzrv5z4va5vikwzutsou", "31aolxoxfpncpajenckhq2yiaqti", "31rtggayns5bzmmztqbqe2lx5y5e", "e5ml1rmymud3lmnikoxc7d2g7", "31lffhvftay2ud23felimxbjcfri", "budshhmcarzee39bobe9qldhv", "31krbxthztddtrd3eksi5rg46jty", "31vwqxd6iet34ljxus3enhdjmrlq", "5atdk8rvuu6f7s52q55itgbha"]


def init_spotify(client_id, client_secret):
    credentials_manager = SpotifyClientCredentials(
        client_id=client_id, client_secret=client_secret)
    return spotipy.Spotify(client_credentials_manager=credentials_manager)


sp = init_spotify(CLIENT_ID, CLIENT_SECRET)

# Connect to SQLite database
conn = sqlite3.connect(DB)
cursor = conn.cursor()

# Load existing IDs from the database


def load_existing_ids(cursor):
    existing_songs = {row[0]
                      for row in cursor.execute('SELECT song_id FROM songs')}
    existing_artists = {row[0] for row in cursor.execute(
        'SELECT artist_id FROM artists')}
    existing_playlists = {row[0] for row in cursor.execute(
        'SELECT playlist_id FROM playlists')}
    return existing_songs, existing_artists, existing_playlists


existing_songs, existing_artists, existing_playlists = load_existing_ids(
    cursor)

# Insert song data into the database


def insert_song(cursor, song_data):
    cursor.execute('''
        INSERT OR REPLACE INTO songs (song_id, song_name, artist_ids, acousticness, danceability, energy,
                                      instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
                                      time_signature, valence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        song_data['song_id'], song_data['song_name'], song_data['artist_ids'],
        song_data['acousticness'], song_data['danceability'], song_data['energy'],
        song_data['instrumentalness'], song_data['key'], song_data['liveness'],
        song_data['loudness'], song_data['mode'], song_data['speechiness'],
        song_data['tempo'], song_data['time_signature'], song_data['valence']
    ))
    existing_songs.add(song_data['song_id'])  # Add to existing_songs set

# Insert artist data into the database


def insert_artist(cursor, artist):
    cursor.execute('''
        INSERT OR REPLACE INTO artists (artist_id, artist_name, artist_genres)
        VALUES (?, ?, ?)
    ''', artist)
    conn.commit()

# Insert playlist data into the database


def insert_playlist(cursor, playlist):
    cursor.execute('''
        INSERT INTO playlists (playlist_id, playlist_creator_id, playlist_original_items, playlist_items)
        VALUES (?, ?, ?, ?)
    ''', playlist)
    conn.commit()

# Update playlist metadata in the database


def update_playlist_metadata(cursor, playlist_id, metadata):
    cursor.execute('''
        UPDATE playlists
        SET playlist_items_fetched = ?,
            playlist_top_artist_ids = ?,
            playlist_top_genres = ?,
            min_acousticness = ?,
            max_acousticness = ?,
            min_danceability = ?,
            max_danceability = ?,
            min_energy = ?,
            max_energy = ?,
            min_instrumentalness = ?,
            max_instrumentalness = ?,
            min_key = ?,
            max_key = ?,
            min_liveness = ?,
            max_liveness = ?,
            min_loudness = ?,
            max_loudness = ?,
            min_mode = ?,
            max_mode = ?,
            min_speechiness = ?,
            max_speechiness = ?,
            min_tempo = ?,
            max_tempo = ?,
            min_time_signature = ?,
            max_time_signature = ?,
            min_valence = ?,
            max_valence = ?
        WHERE playlist_id = ?
    ''', (*metadata, playlist_id))
    conn.commit()

# Scrape Spotify playlist data for a user


def scrape_user_playlists(sp, cursor, user_id):
    try:
        playlists = sp.user_playlists(user_id)

        for playlist in playlists['items']:
            playlist_id = playlist['id']

            if playlist_id in existing_playlists:
                print(f"Skipping playlist {playlist_id} as it already exists.")
                continue

            try:
                playlist_data = sp.playlist(playlist_id)
                playlist_creator_id = playlist_data['owner']['id']
                playlist_items = playlist_data['tracks']['items']

                if len(playlist_items) < 2:
                    print(f"Skipping playlist {
                          playlist_id} because it has fewer than 2 songs.")
                    continue

                track_ids = []
                for item in playlist_items:
                    track = item['track']
                    song_id = track['id']

                    if song_id and song_id not in existing_songs:
                        song_data = extract_song_data(sp, track)
                        if song_data:
                            insert_song(cursor, song_data)

                    track_ids.append(song_id)

                # Insert the playlist data
                insert_playlist(cursor, (playlist_id, playlist_creator_id, len(
                    track_ids), ','.join(track_ids)))
                existing_playlists.add(playlist_id)

            except Exception as e:
                print(f"Error processing playlist {playlist_id}: {e}")

    except Exception as e:
        print(f"Error processing user {user_id}: {e}")

# Extract song data from Spotify API response


def extract_song_data(sp, track):
    try:
        song_id = track['id']
        song_data = {
            'song_id': song_id,
            'song_name': track['name'],
            'artist_ids': ','.join([artist['id'] for artist in track['artists']]),
        }

        # Fetch audio features
        features = sp.audio_features([song_id])[0]
        if features is None:
            return None

        song_data.update({
            'acousticness': features.get('acousticness', 0.0),
            'danceability': features.get('danceability', 0.0),
            'energy': features.get('energy', 0.0),
            'instrumentalness': features.get('instrumentalness', 0.0),
            'key': features.get('key', 0),
            'liveness': features.get('liveness', 0.0),
            'loudness': features.get('loudness', 0.0),
            'mode': features.get('mode', 0),
            'speechiness': features.get('speechiness', 0.0),
            'tempo': features.get('tempo', 0.0),
            'time_signature': features.get('time_signature', 4),
            'valence': features.get('valence', 0.0)
        })
        return song_data
    except Exception as e:
        print(f"Error extracting song data: {e}")
        return None

# Calculate and update playlist metadata in the database


def calculate_and_update_playlist_metadata(cursor, playlist_id):
    cursor.execute(
        'SELECT playlist_items FROM playlists WHERE playlist_id = ?', (playlist_id,))
    result = cursor.fetchone()
    if not result:
        print(f"Playlist {playlist_id} not found in database.")
        return
    song_ids = result[0].split(',')

    # Fetch audio features for all songs in the playlist
    cursor.execute(f'''
        SELECT acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo,
               time_signature, valence, artist_ids
        FROM songs WHERE song_id IN ({','.join(['?'] * len(song_ids))})
    ''', song_ids)
    rows = cursor.fetchall()

    if not rows:
        print(f"No songs found for playlist {playlist_id}.")
        return

    # Initialize min/max variables
    min_acousticness, max_acousticness = float('inf'), float('-inf')
    min_danceability, max_danceability = float('inf'), float('-inf')
    min_energy, max_energy = float('inf'), float('-inf')
    min_instrumentalness, max_instrumentalness = float('inf'), float('-inf')
    min_key, max_key = float('inf'), float('-inf')
    min_liveness, max_liveness = float('inf'), float('-inf')
    min_loudness, max_loudness = float('inf'), float('-inf')
    min_mode, max_mode = float('inf'), float('-inf')
    min_speechiness, max_speechiness = float('inf'), float('-inf')
    min_tempo, max_tempo = float('inf'), float('-inf')
    min_time_signature, max_time_signature = float('inf'), float('-inf')
    min_valence, max_valence = float('inf'), float('-inf')

    # Collect artist and genre information
    artist_counts = {}
    genre_counts = {}

    for row in rows:
        acousticness, danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, time_signature, valence, artist_ids = row

        min_acousticness = min(min_acousticness, acousticness)
        max_acousticness = max(max_acousticness, acousticness)
        min_danceability = min(min_danceability, danceability)
        max_danceability = max(max_danceability, danceability)
        min_energy = min(min_energy, energy)
        max_energy = max(max_energy, energy)
        min_instrumentalness = min(min_instrumentalness, instrumentalness)
        max_instrumentalness = max(max_instrumentalness, instrumentalness)
        min_key = min(min_key, key)
        max_key = max(max_key, key)
        min_liveness = min(min_liveness, liveness)
        max_liveness = max(max_liveness, liveness)
        min_loudness = min(min_loudness, loudness)
        max_loudness = max(max_loudness, loudness)
        min_mode = min(min_mode, mode)
        max_mode = max(max_mode, mode)
        min_speechiness = min(min_speechiness, speechiness)
        max_speechiness = max(max_speechiness, speechiness)
        min_tempo = min(min_tempo, tempo)
        max_tempo = max(max_tempo, tempo)
        min_time_signature = min(min_time_signature, time_signature)
        max_time_signature = max(max_time_signature, time_signature)
        min_valence = min(min_valence, valence)
        max_valence = max(max_valence, valence)

        for artist_id in artist_ids.split(','):
            cursor.execute(
                'SELECT artist_name, artist_genres FROM artists WHERE artist_id = ?', (artist_id,))
            artist = cursor.fetchone()
            if artist:
                artist_name, artist_genres = artist
                artist_counts[artist_name] = artist_counts.get(
                    artist_name, 0) + 1
                for genre in artist_genres.split(','):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1

    # Get top artists and genres
    top_artists = sorted(
        artist_counts, key=artist_counts.get, reverse=True)[:3]
    top_genres = sorted(genre_counts, key=genre_counts.get, reverse=True)[:3]

    # Update playlist metadata
    metadata = (
        len(song_ids), ','.join(top_artists), ','.join(top_genres),
        min_acousticness, max_acousticness,
        min_danceability, max_danceability,
        min_energy, max_energy,
        min_instrumentalness, max_instrumentalness,
        min_key, max_key,
        min_liveness, max_liveness,
        min_loudness, max_loudness,
        min_mode, max_mode,
        min_speechiness, max_speechiness,
        min_tempo, max_tempo,
        min_time_signature, max_time_signature,
        min_valence, max_valence
    )
    update_playlist_metadata(cursor, playlist_id, metadata)
    conn.commit()

# Main script to scrape data for each user's playlists


def main():
    for user_id in user_ids:
        print(f"Scraping playlists for user {user_id}...")
        scrape_user_playlists(sp, cursor, user_id)
        conn.commit()  # Commit changes after each user's playlists are processed

        # Calculate and update playlist metadata for each scraped playlist
        cursor.execute(
            'SELECT playlist_id FROM playlists WHERE playlist_creator_id = ?', (user_id,))
        for (playlist_id,) in cursor.fetchall():
            calculate_and_update_playlist_metadata(cursor, playlist_id)


if __name__ == '__main__':
    main()

# Close the database connection
conn.close()
