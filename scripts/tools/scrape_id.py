import re

text = """
https://open.spotify.com/playlist/6d3rkNwY64ES0qDy1MrW7r?si=695dcfaffbdb42a3 https://open.spotify.com/playlist/2ZnAWYy4AOs8tpRUCGF6Py?si=34bf12431b604056 https://open.spotify.com/playlist/0KGVQ9JLHPz6yfwIqxXJ8z?si=4fae5bbe513446ed https://open.spotify.com/playlist/0GoQedvZwO4jaWgtdZXOEs?si=d3568b12923d44f0 https://open.spotify.com/playlist/37i9dQZF1DX74ozWuOfjjm?si=f210734b04864630 https://open.spotify.com/playlist/53qsotpUUivgdU4F8hfSec?si=c99851f41ccc4cc7 https://open.spotify.com/playlist/30dLtXHfNmXQnrbWDEp6l4?si=eea70762ef9f4ea2









"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
