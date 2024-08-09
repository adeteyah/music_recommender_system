import re

text = """

https://open.spotify.com/playlist/4Nl1jhCaPIq6os4TmbT8rK?si=b51937fc39614573 https://open.spotify.com/playlist/1t6SOFNctZcoElqoD5sNC2?si=809edfaedd3e4ba5 https://open.spotify.com/playlist/3hnkI7OaJS8LBxLNs5RquJ?si=6f043ce62d374af7 https://open.spotify.com/playlist/7KxvTbadcmWVGQJRUj3Pvl?si=59f1830393af46f7 https://open.spotify.com/playlist/61VZ7ZWnpXS6idfynGbU8d?si=2f28420fc54b44f9 https://open.spotify.com/playlist/1Ot7jZOHtMIdRunhkq9VAy?si=2763f0aee05d46f6 https://open.spotify.com/playlist/5YhjEIWz3B8QGIeJFrV9wN?si=eb2268a774e84c52 https://open.spotify.com/playlist/6qu5WqPWhn8z2fQHESan6I?si=908f8e54a29341d0 https://open.spotify.com/playlist/2PclZbmhgjQ1UudVzDzZvg?si=3b4d5428cf734041 https://open.spotify.com/playlist/2kxePmMV4YBzxEOrrUEriU?si=694f835243f34ee8 https://open.spotify.com/playlist/6tSugmKKNj6KlZuj268M5M?si=00cd4fc7bc5245a6 https://open.spotify.com/playlist/6jLofw85SuETJF1Y6Bctw5?si=9c9d0d9ad83b48ab https://open.spotify.com/playlist/1HTstZdJS0ES5LocqyPz0u?si=bd69d95b12e7451d https://open.spotify.com/playlist/5iGR8WjsvOxn7T25kxdxDH?si=5763d87cb83a4b16 https://open.spotify.com/playlist/7qeSVsb8qaRlU49JhlLANt?si=d6c8a0a863f74b4d https://open.spotify.com/playlist/4yjgdCG36M4nuIhDhFLvOQ?si=2872edcbbd604ae3 https://open.spotify.com/playlist/5c9HypEJNtny4plCOhwF7o?si=1bd73bd236e94439 https://open.spotify.com/playlist/3UVEfjeDgjTvBXXwuuPNMu?si=c85230d56ec3426a https://open.spotify.com/playlist/0PAObB8uOVZsOKhhNAsUVA?si=ac2be21e46214218 https://open.spotify.com/playlist/7qzUixjEEw6KL9EZlhHHMc?si=2c78c5bfa9d94f9d









"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
