import re

text = """
https://open.spotify.com/playlist/1yNXopoGHXhYKvnF9ghW6r https://open.spotify.com/playlist/37i9dQZF1DZ06evO2QTIoV https://open.spotify.com/playlist/4ccjnypUiBUKHGKGaDuATg https://open.spotify.com/playlist/0HmEO6swrbowZcizagWzo7 https://open.spotify.com/playlist/0xfFh3DIITXFV3DQzCSTrh https://open.spotify.com/playlist/6wanVv6EsTV8lEnGTldOzb https://open.spotify.com/playlist/6V74xRl4hYX8cmLT7fywrH https://open.spotify.com/playlist/2Z1EcZkCxwVXomQ14VFpdq?go=1&sp_cid=39c47fd9c5ba27ab82e28998df75204b&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/4A4CfD3GgVYyDyKpk7RjJh https://open.spotify.com/playlist/57V7j9vt18lxdRZBthgnUK https://open.spotify.com/playlist/0yMHdtmr7aI2rAW3ZNxvZa https://open.spotify.com/playlist/0QO2mLVcs1OsKF3kVWpRN5 https://open.spotify.com/playlist/18CRyViH5bqzWv8kFCIoKX https://open.spotify.com/playlist/7xBH6HAUcaxLpAK5xv0Gso https://open.spotify.com/playlist/77umv1bBpc8J1LwgF6Z0Zv https://open.spotify.com/playlist/6n4xdTisubdIYrafVyoSqt https://open.spotify.com/playlist/2kaDfCdhq6I572Q3nT1mLS?si=d2fd3044b355411d https://open.spotify.com/playlist/2S6XgJze3XveR81Nh965YP https://open.spotify.com/playlist/13tlYfrCfnY3PODpWTO28z https://open.spotify.com/playlist/0ql0RY0eQbWhm2T4XOnjQ1















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
