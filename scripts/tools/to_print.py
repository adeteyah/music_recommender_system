import re

text = '''
https://open.spotify.com/track/1yKAqZoi8xWGLCf5vajroL My Chemical Romance - The Ghost of You | Genre: emo,modern rock | Acousticness: 0.0286, Danceability: 0.202, Energy: 0.886, Instrumentalness: 0.0, Key: 11, Liveness: 0.643, Loudness: -3.805, Mode: 0, Speechiness: 0.0816, Tempo: 145.781, Time Signature: 4, Valence: 0.192
https://open.spotify.com/track/5dTHtzHFPyi8TlTtzoz1J9 My Chemical Romance - Helena | Genre: emo,modern rock | Acousticness: 0.0142, Danceability: 0.356, Energy: 0.96, Instrumentalness: 0.0, Key: 4, Liveness: 0.209, Loudness: -3.487, Mode: 1, Speechiness: 0.104, Tempo: 125.921, Time Signature: 4, Valence: 0.0857 | COUNT: 21
'''

# Use re to extract the required format
pattern = r'(https://open\.spotify\.com/track/\w+) ([^|]+)'
matches = re.findall(pattern, text)

# Print the header and formatted output
print("header")
for i, match in enumerate(matches, 1):
    print(f"{i}. {match[0]} {match[1].strip()}")
