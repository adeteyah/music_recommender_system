import re

text = """
https://open.spotify.com/playlist/03BXfdy8XI2SiVMcbQ3f8K https://open.spotify.com/playlist/3sc0b961xTbwFnLKDZGwMT













"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
