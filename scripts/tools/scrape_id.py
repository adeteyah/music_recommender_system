import re

text = """
https://open.spotify.com/playlist/6YYoJll65jHxCYVPdkd5CD https://open.spotify.com/playlist/0mh7pPwHuGaDtlyURlhDzE?utm_sq=fmrmmgspzd&utm_source=Facebook&utm_medium=social&utm_campaign=Cleveland+Uniting+Church&utm_content=External+Faith+Resources https://open.spotify.com/playlist/2p0DCsarph7j5s1KAxrHPf?locale=gb&fo=1 https://open.spotify.com/playlist/3peBvggvKVhBf6LOqOFYTW
















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
