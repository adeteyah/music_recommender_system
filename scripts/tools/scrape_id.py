import re

text = """
https://open.spotify.com/playlist/3OGtvL5mc7z1kIK7QUdnx6?si=bdb6fe96b13041e7 https://open.spotify.com/playlist/6XcpGfuYtCpTPSKzpsuPON?si=483fbd43ee8d46c8














"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
