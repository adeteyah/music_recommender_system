import re

text = """
https://open.spotify.com/playlist/4wd6242y2qn44TiCCPX12W?si=1b110b8722bd47c1










"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
