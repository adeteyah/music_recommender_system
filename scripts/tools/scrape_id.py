import re

text = """
https://open.spotify.com/playlist/3UpVooY64Hoh4XcQo9BytP?si=34befc2351674a90 https://open.spotify.com/playlist/0kp7uIVpGp9GMHXqSfcDF8?si=c524a0aca0e54d11 https://open.spotify.com/playlist/0SDuCz9I0l6p5Gp5haENmw?si=c2750cdf1894495d













"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
