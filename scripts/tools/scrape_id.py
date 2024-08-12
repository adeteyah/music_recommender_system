import re

text = """
https://open.spotify.com/playlist/40sNn0bHB6bd0AnogyHoXd https://open.spotify.com/playlist/68Kdkdo67uUtbNn6m2Incn https://open.spotify.com/playlist/5AXoVexX6nykYyVlkZFobP https://open.spotify.com/playlist/72MmIAbC21g5Ge2EsY9qVP https://open.spotify.com/playlist/03NJ2WW9cm04tHLZzgck7N











"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
