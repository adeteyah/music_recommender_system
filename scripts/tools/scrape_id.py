import re

text = """
https://open.spotify.com/playlist/7qlkESHAzMS77g5gRRPPjq https://open.spotify.com/playlist/56fgGUnEurFxPo0TVN4Nb2?go=1&sp_cid=9d3fd151e3052154e089d8c3f6546290&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/3L1FtMJdLbb03cfZY0VZCg https://open.spotify.com/playlist/37i9dQZF1DWXRPjCBAuFj3 https://open.spotify.com/playlist/61ZtcGhXlr0NbFLUxpNSiG https://open.spotify.com/playlist/37i9dQZF1E4wB4mNICRyWd https://open.spotify.com/playlist/5OjJ9uqpYSKnLGJVfRPWub https://open.spotify.com/playlist/7zEWvS6PXlniZTflSTpKln


"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
