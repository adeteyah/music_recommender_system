import re

text = """
https://open.spotify.com/playlist/1yWtg5AOhmCxzvGcc056EL https://open.spotify.com/playlist/1fBvTHcGocxE6KxE6RDwnz https://open.spotify.com/playlist/0EMQj87px54fGDbxw47RVb https://open.spotify.com/playlist/4tUzeaw1JxcsXDZFoL3y8u https://open.spotify.com/playlist/1VnVUXLPvndFF1qdz94VSu?go=1&sp_cid=cde8bc268b4c9b9b1d29e74f5fa58c7e&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/6qclpL3mdUqZsbNigd8gr3 https://open.spotify.com/playlist/6sAhT9rfRtZ1ZX9LnUeaPL https://open.spotify.com/playlist/5q7AgEMBwpd778EDdtgty6?si=cFrQ6Dp-RwmCSLjHkQ8jhg&utm_source=native-share-menu https://open.spotify.com/playlist/3P3tIDy4M3Zs6IPY1aZRSJ https://open.spotify.com/playlist/6vtwdVS7vAu04wHvcKfrZF https://open.spotify.com/playlist/2PAW2efo2RTTvviEQ83efX https://open.spotify.com/playlist/640PALjXsc8byYseP7xutN https://open.spotify.com/playlist/5pQR3inWMW2pt07S1tP0vP https://open.spotify.com/playlist/20PfxVpQLSsugmVnrFUq13 https://open.spotify.com/playlist/2o1OsvXXW4OdjyNeOOeaKk https://open.spotify.com/playlist/16LtCDMg76IJSwrOpeLtm0 https://open.spotify.com/playlist/4JjUy0wuXFZGa8dLgE7Zy4 https://open.spotify.com/playlist/2SevHA2JbHVQMZVq5smdxO https://open.spotify.com/playlist/72l21z0BTQnSL02hzmeZMj https://open.spotify.com/playlist/6YDcTMCA8Un5oWBC7c9L0L

"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
