import re

text = """
https://open.spotify.com/playlist/54fypeptOPWxNNT6yWni9e https://open.spotify.com/playlist/2FqTNl7VcTcW11UjaU29jQ https://open.spotify.com/playlist/3FNNXwsbFZCFxT8JTTHwEs https://open.spotify.com/playlist/4Y7OUsViZav7uUESID82Ij https://open.spotify.com/playlist/2Yeh3LqXsxkIf3DTXjHMcI https://open.spotify.com/playlist/6lnG0UazmVK0nbmsAMnsdb https://open.spotify.com/playlist/4DfNtgZbQVyLaeIrvhqApj https://open.spotify.com/playlist/3ufZE8EWAjqYZtVDYbccVv















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
