import re

text = """
https://open.spotify.com/playlist/74zQbndug04JQOSl8idfIA https://open.spotify.com/playlist/6woZFK1svRjzX59N08UwE0 https://open.spotify.com/playlist/3jltelqHnuWPErD0VUkitM
https://open.spotify.com/playlist/4ROtkOjstuvQ6Rtd3fmXuG?si=7inr_uU_QMqUsBLKRv6Ucw https://open.spotify.com/playlist/1XMcAQ7AgQR2U7NmTKDwq9 https://open.spotify.com/playlist/6VtQR8iKgg4sd48ovbIfef https://open.spotify.com/playlist/6woZFK1svRjzX59N08UwE0 https://open.spotify.com/playlist/1ldFIzTyLgksmjmhikrq0e https://open.spotify.com/playlist/1XMcAQ7AgQR2U7NmTKDwq9 https://open.spotify.com/playlist/4MAg9d3hT7ZxCysc3MUQcA https://open.spotify.com/playlist/4jTSiPeCp86RXXAj37tQqc https://open.spotify.com/playlist/3SppVKB3kfT6rbElEi9Lsy https://open.spotify.com/playlist/3sdumc7gqOViCbmESNXEJv https://open.spotify.com/playlist/7xTDTQ5ZFFA4xig2I4KLx8







"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
