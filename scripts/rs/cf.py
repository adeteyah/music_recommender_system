import os
import csv
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')


def load_data(directory_path):
    data = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory_path, filename)

            # Extract creator_id and playlist_id from the filename
            base_filename = os.path.splitext(filename)[0]
            creator_id, playlist_id = base_filename.split('_')

            with open(file_path, 'r', newline='') as csvfile:
                csvreader = csv.DictReader(csvfile)
                for row in csvreader:
                    # Add creator_id and playlist_id to each row dictionary
                    row['creator_id'] = creator_id
                    row['playlist_id'] = playlist_id
                    data.append(row)
    return data


def cf_result(ids):
    def generate_recommendations(playlists, ids):
        matched_playlists = []
        for playlist in playlists:
            if playlist.get('spotify_id') in ids:
                matched_playlists.append(playlist)
        return matched_playlists

    playlists = load_data(config['dir']['transformed'])
    print(f"Loaded {len(playlists)} rows of data from playlists CSV.")

    # Print the first few playlists to check their structure
    print("Sample playlist data:")
    for playlist in playlists[:5]:  # Print the first 5 playlists as a sample
        print(playlist)

    matched_playlists = generate_recommendations(playlists, ids)

    # Prepare formatted recommendation text
    formatted_recommendations = []
    for playlist in matched_playlists:
        formatted_recommendations.append(f"https://open.spotify.com/artist/{playlist['creator_id']} - https://open.spotify.com/track/{
                                         playlist['spotify_id']} | Playlist https://open.spotify.com/playlist/{playlist['playlist_id']} by Creator https://open.spotify.com/user/{playlist['creator_id']}")

    # Write formatted recommendations to a text file
    with open('cf_recommendation.txt', 'w') as file:
        file.write("\n".join(formatted_recommendations))

    return f"Stored result on {ids}!"


if __name__ == "__main__":
    ids = ['1uCDg9WDXzG5j1tVqnFNBR']
    result = cf_result(ids)
    print(result)
