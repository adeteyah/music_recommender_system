import configparser
import requests
import base64


def load_config(config_file='config.cfg'):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config


def get_access_token(client_id, client_secret):
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + base64.b64encode((client_id + ":" + client_secret).encode()).decode()
    }
    data = {
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()  # Ensure we catch errors
    return response.json()["access_token"]


def get_recommendations(access_token, seed_tracks):
    url = "https://api.spotify.com/v1/recommendations"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "seed_tracks": ",".join(seed_tracks),
        "limit": 20  # Change this to get more recommendations if needed
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()


def print_recommendations(song_id, recommendations):
    print(f"SONG {song_id} ({recommendations['tracks'][0]['artists'][0]['name']} - {
          recommendations['tracks'][0]['name']} and link: {recommendations['tracks'][0]['external_urls']['spotify']})")
    print("1. recommendation item (artist - title and link)")
    for idx, track in enumerate(recommendations['tracks'], start=1):
        artist_name = track['artists'][0]['name']
        track_name = track['name']
        track_link = track['external_urls']['spotify']
        print(f"{idx}. {artist_name} - {track_name} (link: {track_link})")


# Main script
config = load_config()
CLIENT_ID = config['api']['client_id']
CLIENT_SECRET = config['api']['client_secret']

# Get an access token
access_token = get_access_token(CLIENT_ID, CLIENT_SECRET)

# Input song IDs
song_ids = [
    '37F0uwRSrdzkBiuj0D5UHI',
    '3pCt2wRdBDa2kCisIdHWgF',
    '3ymuBMTviroWLuf1jMsMVf',
]  # Replace with actual song IDs

# Fetch and print recommendations for each song ID
for song_id in song_ids:
    recommendations = get_recommendations(access_token, [song_id])
    print_recommendations(song_id, recommendations)
    print()  # Add a blank line between each song's output
