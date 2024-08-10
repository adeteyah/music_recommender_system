import re

text = """

https://open.spotify.com/playlist/022fvQXuJQDeACz9mUkDFw?si=bc9c912093224fd9 https://open.spotify.com/playlist/5vSCsBRotGGzEMI3lr9Kk6?si=d3614f9b17774773 https://open.spotify.com/playlist/4DhYEdh4Oj7CzijDcD99tk?si=58854a3148a24c8d https://open.spotify.com/playlist/2QxrPkOTlVdtY8HU0ohlNb?si=4be0546aeefb4c7a https://open.spotify.com/playlist/4FcSwayjqyAnQytCzcnpIT?si=6b1e61d790484c3e https://open.spotify.com/playlist/2Wwoknwx4fyX8OpL8ePtNT?si=0f550c06b8e640a2 https://open.spotify.com/playlist/2JxUwUXaY8OhgfIuozMcG2?si=cf7c2527495e452d https://open.spotify.com/playlist/7h3lfQ3r6XGAvbNM3kquXX?si=4a92960134cf4b61 https://open.spotify.com/playlist/3qCLY1QE58gwSrpRS18osm?si=8f546013f412481d https://open.spotify.com/playlist/2JxUwUXaY8OhgfIuozMcG2?si=6f2e1967771b47d1





"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
