import re

text = """
https://open.spotify.com/playlist/2BTilOTjx1JW5rIzS9UvUZ?si=1b1417aa576d4473 https://open.spotify.com/playlist/1UzF1UBbG7n7BMkZooZ1gT?si=0ea9e495d2bf4158 https://open.spotify.com/playlist/0fWsAt5G2vmDXGY0KuCtZz?si=f36172af268346ba https://open.spotify.com/playlist/5qDySCjaeRmGpjpD5469T2?si=ed6154d25e004689 https://open.spotify.com/playlist/6ECCI8opmVsXYtBfixdsST?si=421c80e34535408e








"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
