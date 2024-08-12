import re

text = """
https://open.spotify.com/playlist/2bBvREgXS9hVzItzLAP3Ai?si=ea05f5df34144a31 https://open.spotify.com/playlist/4N4MjwNw4YD0CxsNEwZ8Ln?si=f3273867b6934983 https://open.spotify.com/playlist/6jUNgBrw01aOm6uTri6HZb?si=3fcbd0f777434a1c









"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
