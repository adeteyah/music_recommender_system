import re

text = """

https://open.spotify.com/playlist/0l22l55XLkuMRPVUYjJgsq?si=9a8109a20b8d4aa0 https://open.spotify.com/playlist/6yUre9x8VDiMt26juJrmwF?si=c9672227102944ec https://open.spotify.com/playlist/2H08R9qQtDqy8ZQ9v3eTqH?si=de3ddfec4e4441a1 https://open.spotify.com/playlist/0XCcXjAm5L7ja0tzE2btY5?si=d19422b2a4234c40 https://open.spotify.com/playlist/31GKKtlZP6eOo1PSmjD0aF?si=5e07d3853b8d4f68 https://open.spotify.com/playlist/7tPX9t6GnVPkdDZddKFilx?si=f162b794f5134875 https://open.spotify.com/playlist/7IlhhKTvGMLAIJcG2eQ8eC?si=6dc4dfbda1d447f9 https://open.spotify.com/playlist/6igRcv84LxVddaeFywbHGb?si=bd75e2eec271468b https://open.spotify.com/playlist/0ZQZoJOXPeO5tdOvA1yab6?si=97ab503acc914cce https://open.spotify.com/playlist/4r4bvzuNI2OAGQjdGSlxnD?si=a601f230709f4404 https://open.spotify.com/playlist/2arcOLGvZNkIRSYNRgndsn?si=77ab905bfaea42ff https://open.spotify.com/playlist/6Mqy35UoaxavnPHlIavLa6?si=44dd9df068e64fc8 https://open.spotify.com/playlist/2XVgEo6IkJoQHsT47lxOpy?si=d2f248297d9f483a










"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
