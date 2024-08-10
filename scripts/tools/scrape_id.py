import re

text = """

https://open.spotify.com/playlist/1Hk4si22NV4TW0RDLcCdRG https://open.spotify.com/playlist/3oCfnySxTQekvcKUH40XVQ https://open.spotify.com/playlist/0T3gfPSkP2be5qHij1LOd5?si=33a57c7523364813 https://open.spotify.com/playlist/1t6SOFNctZcoElqoD5sNC2?si=d142059bd5f24fff https://open.spotify.com/playlist/1yBCx8xJgXEIJ9HrNvclr0?si=58342643ca6746a7 https://open.spotify.com/playlist/6z9SVGrNP6YtIqb6z9ESrZ?si=9078313ac11e4159


"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
