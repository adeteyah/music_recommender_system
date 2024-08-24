import re

text = """
https://open.spotify.com/playlist/3vcQlgb87xCxHrIckUza23  https://open.spotify.com/playlist/6vXnkOX31XW9mtzIwGZpSI https://open.spotify.com/playlist/0X1onDnCUQJzrSy1BM98IO https://open.spotify.com/playlist/1pBwPCU7r6JZepffwVbhGm https://open.spotify.com/playlist/5NTHYsO6nwYu0jVEnymi40 https://open.spotify.com/playlist/5OaIxOYHwxGGM7wjpGpLlP https://open.spotify.com/playlist/779iLhzoPQSF3Vb9AuiFTZ https://open.spotify.com/playlist/3FI2diqm8PoUIOeU0QjrUQ https://open.spotify.com/playlist/7k3QVpiARhGze7Elp5HlkF https://open.spotify.com/playlist/551itYPVoMP3DovzDyk8xK https://open.spotify.com/playlist/4UTvZBu04lpLMyPcTVo2dt https://open.spotify.com/playlist/6bn8qJ6MwNNBHmkXkhPVuw https://open.spotify.com/playlist/3cnMbJ2EvwZ9SX1WXPPa2M
















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
