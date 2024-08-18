import re

text = """
https://open.spotify.com/playlist/65W5c6tHMl3J5Af8SmWV3c https://open.spotify.com/playlist/4GLP57gMtuw3k6y1tNz1PN https://open.spotify.com/playlist/2BMdQu1rDpMtXM91B3jClS https://open.spotify.com/playlist/5bmQ4nGngYUN0cHf01VRPa https://open.spotify.com/playlist/6GTlkQXnqZylQQou0SR3E1 https://open.spotify.com/playlist/6rLmHjDSDshQ7AgNNvnMF9?go=1&sp_cid=de85445594ac8aadee5d2460f3ecc2aa&intent=addToLibrary&utm_source=embed_player_v&utm_medium=desktop https://open.spotify.com/playlist/09Nh9lKyelPWWYePQRjqI5 https://open.spotify.com/playlist/3lpCRmNOO3eepOsifudXQh https://open.spotify.com/playlist/2E6fOraA1wbcvsCxHL3F1E https://open.spotify.com/playlist/257v1jXwmN4Uq1DRphtLhG https://open.spotify.com/playlist/5BxqiXdL315dDipxbfKXdr https://open.spotify.com/playlist/1PlfoubR8xBIqIx15tjXwR











"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
