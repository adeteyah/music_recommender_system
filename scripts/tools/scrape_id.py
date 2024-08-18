import re

text = """
https://open.spotify.com/playlist/6Q9NaA5dVrgG7EIo0DpQdP https://open.spotify.com/playlist/2jLmLbu3MnTN4UMZHIE7Ca https://open.spotify.com/playlist/06fzulovcu9GJ0g1DOnh9e

https://open.spotify.com/playlist/5v6Bjrs134akMmwpU3n57P https://open.spotify.com/playlist/4KwtkU1RQbEIqUBVbsURiQ https://open.spotify.com/playlist/0tIalBclB1VV6UjuQ3ggFF https://open.spotify.com/playlist/282JOVQjz6jNFP793hmkEG https://open.spotify.com/playlist/19MUCaiylLBhugLIyTpC48 https://open.spotify.com/playlist/6rfrlUG6dmvJIl5vfVWkCN https://open.spotify.com/playlist/5iL6oIdZWvh2p0p2PBZg2X






"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
