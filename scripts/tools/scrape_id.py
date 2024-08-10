import re

text = """


https://open.spotify.com/playlist/7sMerhMCG0DGLTHJg3wxnx?si=1d7f5dd4e1f14cad











"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
