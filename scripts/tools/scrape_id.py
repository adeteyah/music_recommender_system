import re

text = """
https://open.spotify.com/playlist/0P3ieWY6Ri33FzP1suHakC?go=1&sp_cid=a4a40a3999a979f7b5cb2bfe719bf5e3&intent=addToLibrary&utm_source=embed_player_v&utm_medium=desktop  https://open.spotify.com/playlist/4jioZ6p2ZdZuNWlkCS5OXa https://open.spotify.com/playlist/55M6sFoow7KjS9tz0CSZxw
https://open.spotify.com/playlist/5WqHfJDRG5Gmyw65LR8Uqo

"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
