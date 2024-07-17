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


def generate_recommendations(playlists, exclude_ids, limit=10):
    # Example: Exclude specified IDs, or implement your own logic to filter recommendations
    recommendations = []
    for playlist in playlists:
        if playlist['spotify_id'] not in exclude_ids:
            recommendations.append(playlist)
            if len(recommendations) >= limit:
                break
    return recommendations


def cf_result(ids):
    playlists = load_data(config['dir']['transformed'])

    # Generate recommendations excluding the input IDs
    matched_playlists = generate_recommendations(playlists, ids)

    # Prepare formatted recommendation text
    formatted_recommendations = []
    for playlist in matched_playlists:
        formatted_recommendations.append(f"https://open.spotify.com/artist/{playlist['creator_id']} - https://open.spotify.com/track/{
                                         playlist['spotify_id']} | Playlist https://open.spotify.com/playlist/{playlist['playlist_id']} by Creator https://open.spotify.com/user/{playlist['creator_id']}")

    # Write formatted recommendations to a text file
    with open('cf_recommendation.txt', 'w') as file:
        file.write("\n".join(formatted_recommendations))

    return f"Stored result on {len(matched_playlists)} recommendations!"


if __name__ == "__main__":
    # Input IDs to exclude from recommendations
    ids = ['4XTP6QLsMZ1GQe0c1i1Oze']
    result = cf_result(ids)
    print(result)
