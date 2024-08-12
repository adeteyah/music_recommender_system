import re

text = """
https://open.spotify.com/playlist/2U93z3XwgloCLKUxCeEeC7?si=7fcafd0430734ebe https://open.spotify.com/playlist/32TI2TcwsaCGYDHRPJ3E4Q?si=c3f8d8f9a94f433b https://open.spotify.com/playlist/2Kraj9XqdTfMbgi34fqkO4?si=7b0bbed51cc94708 https://open.spotify.com/playlist/4NV5D6dgNLOjz2lbFKdgkI?si=1ea4934ff0b54253 https://open.spotify.com/playlist/3xwTlZ84dOxTndQ5RJoSJo?si=db23a6e4abe24f1b https://open.spotify.com/playlist/47hyUd6IQEifuqUutXx2cV?si=a08468725f8649f1 https://open.spotify.com/playlist/7EG6iRHaXIcCqrsE03o5wn?si=b0656956fb2c4464 https://open.spotify.com/playlist/4VvtboJIC2bs1frt033zKC?si=87c35ea90e334792

















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
