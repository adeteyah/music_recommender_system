import re

text = """

https://open.spotify.com/playlist/5sVKi9BlHtT3Daz6QrosgO?si=d9896c1365b54850 https://open.spotify.com/playlist/4cVibuAVfrfiwwZaHGpBzd?si=6be8aa0de3e94453 https://open.spotify.com/playlist/37i9dQZF1DXdOEFt9ZX0dh?si=d0a0b7abb65a4bae https://open.spotify.com/playlist/37i9dQZF1DWSlJG7YPUBHF?si=92e6e2ab4aed4ddc https://open.spotify.com/playlist/0gsHnxZXeIsuUl1qNhe680?si=2cf34fbfa95045f5 https://open.spotify.com/playlist/2YUrwFGp79hwJR0JQkoypc?si=1fef6f39c3e14057 https://open.spotify.com/playlist/3ARB40alcAJh1XOz17EXlz?si=a09bed3815ae4776 https://open.spotify.com/playlist/5P1LoubIeb1LOEVzzP48xs?si=a28ed7ed56974d88 https://open.spotify.com/playlist/1ti3v0lLrJ4KhSTuxt4loZ?si=7eb44212747f4ab3 https://open.spotify.com/playlist/37i9dQZF1DWWwzidNQX6jx https://open.spotify.com/playlist/1b3joOKPxGmE6Hrslwe9vf https://open.spotify.com/playlist/6efKLC9RpAC2gDf2EN1taB https://open.spotify.com/playlist/4gsDnjrEQStNNWCfYa84xW https://open.spotify.com/playlist/37i9dQZF1E4vamD0rbgmqu https://open.spotify.com/playlist/37i9dQZF1E8Nv9MtoW0Uxj https://open.spotify.com/playlist/7m4eG1zlBivIYBZxZg8yOG?go=1&sp_cid=67e34e25ec5c56fbcfdafb25e22f753c&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/7sGPMP0SVOmtmLSaK1Yh6c?go=1&sp_cid=9d848b7eab9cd116ac77792ba8927007&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/0a7nXzXywOKn2tAAjOmeVd https://open.spotify.com/playlist/6yKloPSTrCreBUNuVjRQAl https://open.spotify.com/playlist/2TLwMiJkqXJ8BBTCZjgqSE https://open.spotify.com/playlist/72844CKV8LUcaUgNOQtdrt https://open.spotify.com/playlist/5KTmaOBfHqg8agvNVYv4aI https://open.spotify.com/playlist/5e3S8wlHFW3c2K21VmJjdg https://open.spotify.com/playlist/51HnfVZhDqNNcjRMbL8h5j https://open.spotify.com/playlist/74gSJ8AmV4WDzDGIfvFZdu https://open.spotify.com/playlist/4RTsNbOE6cFgQMupXhc6gB https://open.spotify.com/playlist/4e1htxlM4WKgCBqspme7Kc https://open.spotify.com/playlist/7pzMYtP0t7ld7hITNCH2Jf https://open.spotify.com/playlist/0luHQolnbveBEXsj3WW1l5 https://open.spotify.com/playlist/2FCPM07oMv1XfeLzpTuFMo https://open.spotify.com/playlist/4O9bZQntAOKtZ9wwbEqc3Y https://open.spotify.com/playlist/1DTzz7Nh2rJBnyFbjsH1Mh https://open.spotify.com/playlist/56tOjxTUlvcop1yZnerEsV https://open.spotify.com/playlist/1hNUwJr4JcwOajMW3jvxKJ https://open.spotify.com/playlist/5QfeuAJDN0sZx5nXObX5zh https://open.spotify.com/playlist/2IHFQUnXfczv6xMN1ngoTM https://open.spotify.com/playlist/1ER4OXxuabmEj4mCkHhtSj https://open.spotify.com/playlist/568i4laaPaKgAnGnncqaK4 https://open.spotify.com/playlist/3HCNbrCNWynKAin60X6ekd https://open.spotify.com/playlist/4TV1Fz6cywDWkbBNv0jmrb https://open.spotify.com/playlist/3xT08jqNcxc0wjssR9kBCp https://open.spotify.com/playlist/5KRfnjWU923Iig3suLQ2ej https://open.spotify.com/playlist/11DwMHyVyoucETQXk5L35F?go=1&sp_cid=e6f5f78fd8efe765a662dfea1a08bed0&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/0iacCEUX11kHZIZsxHzbN6 https://open.spotify.com/playlist/5Vfd9w0BIlZj99J9x4ARfO https://open.spotify.com/playlist/7K8Bo6bK65G5RDFiIpiHun https://open.spotify.com/playlist/7LgxKW1WN8jUGRnPVHfT1w https://open.spotify.com/playlist/52y2cEytIHoR6ZTQA4DSNj








"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
