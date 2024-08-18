import re

text = """
https://open.spotify.com/playlist/6JyjhrRZ8kTpkGzHnsxwSf https://open.spotify.com/playlist/6JyjhrRZ8kTpkGzHnsxwSf https://open.spotify.com/playlist/54HdjEBtiCdi39cY7ibR0E














"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
