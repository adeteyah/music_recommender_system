import os
import csv
import configparser

config = configparser.ConfigParser()
config.read('config.cfg')


def cf_result(ids):
    def load_data(directory_path):
        data = []
        for filename in os.listdir(directory_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(directory_path, filename)
                with open(file_path, 'r', newline='') as csvfile:
                    # Use DictReader to directly get dictionaries
                    csvreader = csv.DictReader(csvfile)
                    for row in csvreader:
                        data.append(row)
        return data

    def generate_recommendations(playlists, ids):
        matched_playlists = []
        for playlist in playlists:
            if playlist.get('spotify_id') in ids:
                matched_playlists.append(playlist)
        return matched_playlists

    def write_recommendations():
        pass

    playlists = load_data(config['dir']['transformed'])
    print(f"Loaded {len(playlists)} rows of data from playlists CSV.")

    # Print the first few playlists to check their structure
    print("Recommendations:")
    for playlist in playlists[:50]:  # Print the first 5 playlists as a sample
        print(playlist)

    matched_playlists = generate_recommendations(playlists, ids)
    for playlist in matched_playlists:
        print(f"Matched playlist: {
              playlist['name']} (Spotify ID: {playlist['spotify_id']})")

    return f"Stored result on {ids}!"


if __name__ == "__main__":
    ids = ['7rRKhAve6D9RtIZdk5qtX8']
    result = cf_result(ids)
    print(result)
