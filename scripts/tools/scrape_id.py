import re

text = """
https://open.spotify.com/playlist/7dWLVHhleHDOAmrkVBhjTd?si=6d1b525ecd214be8 https://open.spotify.com/playlist/0iEa8RI9T1zPq8JGyBOG3s?si=4752106c8e164a86 https://open.spotify.com/playlist/6IlRk24OGS1E9tJxlMRJSm?si=eb3647f02d9f457d https://open.spotify.com/playlist/4Vg2jXWBQSfIZ8HxbgML2z?si=f40da3420a734924 https://open.spotify.com/playlist/4vlFxQcbQdfQ2N9Tw1IlOD?si=ba048b404a6a4ea4 https://open.spotify.com/playlist/6khtj4WNmXgY1udUYXwaoe?si=ba2cff72cb3740c3 https://open.spotify.com/playlist/37i9dQZF1E4y8NHHXWtyhk https://open.spotify.com/playlist/0JJVVlPPkcKFN5BikIrmA1 https://open.spotify.com/playlist/5Lo7a936yE5kqutpNt4i7c https://open.spotify.com/playlist/3yuhAxr6DzD8G9RxdWZq9F https://open.spotify.com/playlist/4yKAiganW8SkHI7gGox52U https://open.spotify.com/playlist/3INYq8oYRfF0v6I86ym9B2





"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
