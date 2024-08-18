import re

text = """
https://open.spotify.com/playlist/2QWMrIYAncJzfic0azi6eY https://open.spotify.com/playlist/3rLoX30DD6xuPzeoiUPGFA https://open.spotify.com/playlist/3lwKWtF0WgDUD9EySnywqZ?lf=&icon=play https://open.spotify.com/playlist/3ybC8Xi1uXYLgjUoWO5oSW?si=8029b2e88f8b4605 https://open.spotify.com/playlist/4qxjSmSSmXMZXJTymbbq3t https://open.spotify.com/playlist/3gP1iTYZC5EkhhiJ0hfOd2










"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
