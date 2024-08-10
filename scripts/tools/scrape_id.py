import re

text = """
https://open.spotify.com/playlist/4QGUHviS3DILPEIY3pr4vV?si=c4e0b4b8b3fd451d https://open.spotify.com/playlist/7oKfi7K8WUOetawBJGuUNV?si=ccc0bbb5809348a1 https://open.spotify.com/playlist/1F4SkGrLM2IIux7TSoSGY7?si=ba8bc96e15b44b2a https://open.spotify.com/playlist/2it5i6BVpH4DYJLROfdAWz?si=a4cc7a6d6fd541e8 https://open.spotify.com/playlist/6R289Js63LzdasMGQfATub?si=b232faf97e6049c1 https://open.spotify.com/playlist/62bQfeMgV6b1HAZkK4moGK?si=e366032c9c524d12 https://open.spotify.com/playlist/2E8UqyyJIjylb5YTvvRZMM?si=fd36fe512a9a4b07 https://open.spotify.com/playlist/3U9eNgeDJVOGvzB1p3tghQ?si=67a1824cc62a4070 https://open.spotify.com/playlist/3XF957ddALWqbfXkbNsP5l?si=2e0e133ed45c4188 https://open.spotify.com/playlist/5jo2aWgpyDOjusbVLvaGzc?si=327fe9bb8bf34e6b https://open.spotify.com/playlist/01RXJbRpOHQxM1aWTucark?si=5d915b37c28f4a4c https://open.spotify.com/playlist/6faz8QGOyWuKCr0ly5zM0k?si=894ea8d14967480e















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
