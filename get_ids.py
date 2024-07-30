import re

text = """
https://open.spotify.com/track/6EIMUjQ7Q8Zr2VtIUik4He?si=30d2c1e7b20642b8 
https://open.spotify.com/track/3wlLknnMtD8yZ0pCtCeeK4?si=0ad4e667712e42ed


"""
user_pattern = re.compile(
    r"track/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
