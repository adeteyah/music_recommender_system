import re

text = """


https://open.spotify.com/playlist/3ErsNWUyTyfBk5BKVbQqwA








"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
