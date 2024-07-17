import os
import pandas as pd
from collections import defaultdict


def load_playlist_data(folder_path):
    """
    Load playlist data from CSV files in the specified folder.
    Assumes file names are in the format 'creator_id_playlist_id.csv'.
    Returns a dictionary where keys are creator_id and values are lists of playlist IDs.
    """
    playlist_data = defaultdict(list)

    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            creator_id, playlist_id = filename.split(
                '_')[0], filename.split('_')[1].split('.')[0]
            playlist_data[creator_id].append(playlist_id)

    return playlist_data


def find_playlists_with_ids(playlist_data, input_ids):
    """
    Find playlists that contain the specified input IDs.
    Returns a dictionary where keys are creator_id and values are lists of matching playlist IDs.
    """
    playlists_with_ids = defaultdict(list)

    for creator_id, playlist_ids in playlist_data.items():
        for playlist_id in playlist_ids:
            playlist_df = pd.read_csv(
                f"data/transformed/{creator_id}_{playlist_id}.csv")
            if any(id in playlist_df['track_id'].values for id in input_ids):
                playlists_with_ids[creator_id].append(playlist_id)

    return playlists_with_ids


def recommend_tracks(playlist_data, playlists_with_ids, input_ids):
    """
    Generate track recommendations from playlists that contain the input IDs.
    Exclude the input IDs themselves from recommendations.
    """
    recommendation_counts = defaultdict(int)

    for creator_id, playlist_ids in playlists_with_ids.items():
        for playlist_id in playlist_ids:
            playlist_df = pd.read_csv(
                f"data/transformed/{creator_id}_{playlist_id}.csv")
            recommended_tracks = playlist_df[~playlist_df['track_id'].isin(
                input_ids)]['track_id'].tolist()
            for track_id in recommended_tracks:
                recommendation_counts[track_id] += 1

    sorted_recommendations = sorted(
        recommendation_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_recommendations


def calculate_contribution_stats(playlists_with_ids):
    """
    Calculate contribution stats of playlists based on how many times they contribute to recommendations.
    """
    contribution_stats = []
    total_playlists = sum(len(ids) for ids in playlists_with_ids.values())

    for creator_id, playlist_ids in playlists_with_ids.items():
        percentage = (len(playlist_ids) / total_playlists) * 100
        contribution_stats.append(f"Playlist {playlist_ids} from {
                                  creator_id} contributed ({percentage:.2f}%) to the RS")

    return contribution_stats


# Example usage:
if __name__ == "__main__":
    input_ids = ['26eV0R7nbqtlzh316ncU99']
    folder_path = "C:/Users/Adeteyah/Documents/music_recommender_system/data/transformed"

    # Step 1: Load playlist data
    playlist_data = load_playlist_data(folder_path)

    # Step 2: Find playlists with input IDs
    playlists_with_ids = find_playlists_with_ids(playlist_data, input_ids)

    # Step 3: Generate recommendations
    recommendations = recommend_tracks(
        playlist_data, playlists_with_ids, input_ids)

    # Step 4: Calculate contribution stats
    contribution_stats = calculate_contribution_stats(playlists_with_ids)

    # Print results
    print("Inputted IDs:")
    for i, track_id in enumerate(input_ids, start=1):
        print(f"{i}. {track_id}")
    print("\nSongs recommendations (100 items):")
    for i, (track_id, _) in enumerate(recommendations[:100], start=1):
        print(f"{i}. {track_id}")
    print("\nStats: (sort descending)")
    for stat in contribution_stats:
        print(stat)
