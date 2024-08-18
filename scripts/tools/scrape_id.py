import re

text = """
https://open.spotify.com/playlist/2cBndPFgLHzMuXeOqHUKfN?si=55125cc1c9bf477c
https://open.spotify.com/playlist/1jS9fKqZ4VooOVmf6IbGNm?si=ecd7d0ec45c7410a



"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
