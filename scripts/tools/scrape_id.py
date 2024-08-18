import re

text = """
https://open.spotify.com/playlist/7IwPwJYJYUmEno5LVvmJNm https://open.spotify.com/playlist/1WF0oldV2g5EOww54LEsE6 https://open.spotify.com/playlist/4f2XyEPUu8a8n2xBRMEBwC https://open.spotify.com/playlist/2wJJQfU6wo0MbvXLRJhdVB


"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
