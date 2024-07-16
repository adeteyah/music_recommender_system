import re

text = """

https://open.spotify.com/user/piqxil?si=4ecd30cf490b43d4https://open.spotify.com/user/1213191842?si=4a3dee94c9e647c8https://open.spotify.com/user/5s9u48xridz8gkkwwmvrkdo3c?si=04588b9da17e4f70
https://open.spotify.com/user/arliputrisa?si=6a62afce10284eda

"""

# Regex to find Spotify usernames in the URLs
user_pattern = re.compile(r"https://open\.spotify\.com/user/([a-zA-Z0-9]+)")

# Find all matches
matches = user_pattern.findall(text)

# Remove duplicates
unique_usernames = list(set(matches))

# Print the unique usernames in numbered list format
print(unique_usernames)