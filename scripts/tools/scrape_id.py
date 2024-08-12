import re

text = """
https://open.spotify.com/playlist/2Vi2H4BhJVG0PFnzYB8sgb https://open.spotify.com/playlist/2Vi2H4BhJVG0PFnzYB8sgb https://open.spotify.com/playlist/20R8anptqFQTGk4P2X6dRp https://open.spotify.com/playlist/5p2Z31GzqJruqYlZXj8Poj https://open.spotify.com/playlist/7K5i9JD92Shn7A5MWh7h4v https://open.spotify.com/playlist/37i9dQZF1E4vbz4swHVKWX https://open.spotify.com/playlist/37i9dQZF1EIXNLRz8j6IGJ



















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
