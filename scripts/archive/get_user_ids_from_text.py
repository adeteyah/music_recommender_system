import re

text = """
https://open.spotify.com/user/hicklint?si=177f4dd736f147eehttps://open.spotify.com/user/21noawqda6gejq3niwdppdmzi?si=1c0ec59d0d804c0bhttps://open.spotify.com/user/tomtemplar42?si=6d53bbf803124b0a
"""

user_pattern = re.compile(r"https://open\.spotify\.com/user/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
