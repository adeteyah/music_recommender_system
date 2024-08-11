import re

text = """
https://open.spotify.com/playlist/6JISVM2jY9cSIDg0JGxhpO?si=64241116e7c6487d https://open.spotify.com/playlist/3dClDOdwkwIBXBl0E9oGfQ?si=2aa86f5c1a64490b https://open.spotify.com/playlist/0nJTYwbU6VgewYBwYVQBqS?si=13424384c28f4986 https://open.spotify.com/playlist/5m0ZeXgYo0uwKRgmkmjWQU



"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
