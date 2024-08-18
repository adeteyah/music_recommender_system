import re

text = """
https://open.spotify.com/playlist/2Qe07wVBefgFY6yakMauVa https://open.spotify.com/playlist/0JAhRTi954JdzbPCunoDFy https://open.spotify.com/playlist/0C42S52JylueMmjD4vTFvY https://open.spotify.com/playlist/0xUQa3gRPshqHGwYek1sbr https://open.spotify.com/playlist/3Lf9PqUBWQMeOtfuCNPnoY https://open.spotify.com/playlist/7EaYtgXsI7HXMWaL71wXBE









"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
