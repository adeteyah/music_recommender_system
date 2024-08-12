import re

text = """
https://open.spotify.com/playlist/2BTilOTjx1JW5rIzS9UvUZ?si=1b1417aa576d4473








"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
