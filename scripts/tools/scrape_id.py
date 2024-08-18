import re

text = """
https://open.spotify.com/playlist/18fxVV3YtRFOicZmc4TYrE?autoplay=true  https://open.spotify.com/playlist/0npiegxzaLDMnsUP6xjPM6
https://open.spotify.com/playlist/5oz5Yj6Je19PSDQiS0L5BH?si=43bdc2692cd8465a https://open.spotify.com/playlist/2e84GxTXVSZ9Mbu022reFH?si=3711c70644964674 https://open.spotify.com/playlist/7iCx15Dx4CgkoJwsIB20pS?si=13d55da9c7104b5a https://open.spotify.com/playlist/5D1hIpKWuykE3uMNtd1qdE?si=761c06ac2db94a43 https://open.spotify.com/playlist/6CRjIsydbnZjCjtCMrkq6G?si=45519845dc7d4267 https://open.spotify.com/playlist/7eOqWHRA60tl970P8CnDQU?si=2ee3aef31ffa4f49 https://open.spotify.com/playlist/448x7MjIEF8A5DR2mvLdiz?si=27b10a1c2d6d438d



"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
