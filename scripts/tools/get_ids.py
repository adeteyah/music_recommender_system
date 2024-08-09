import re

text = """
https://open.spotify.com/playlist/0s6CEeemXPec7wUMStvJQP?si=00e34fc997144a14 https://open.spotify.com/playlist/6MnLPuVGrV1MH0f2s4FkjB?si=8804c9811e8a4be9 https://open.spotify.com/playlist/11X76c5MphTG1VgKmC7hgb?si=6218c8a2b83d4fef https://open.spotify.com/playlist/1wlcbdQwkltllE502f3uPr?si=0891b12e59eb42c6 https://open.spotify.com/playlist/4cIPf8YIp2U9XltRhBox7t?si=0a623b325d7344e6 https://open.spotify.com/playlist/2ZpSU8WHjNcNqsRWoBqHNg?si=e24920b21a5a41c4 https://open.spotify.com/playlist/49qtYZo1UzUaghvZ2QuQMs?si=408e155bcca141bf https://open.spotify.com/playlist/4VpMhGgwJ8r8EDGTDTbeer?si=d59f6543ee844659 https://open.spotify.com/playlist/2nzVCXza1cHdl0jk7vmdNQ?si=7a1bec0378fe4fb0 https://open.spotify.com/playlist/1V4QL33vsALvljElabTpxq?si=5588de1fbc8f446f https://open.spotify.com/playlist/7qeSVsb8qaRlU49JhlLANt?si=aed0e4e8723a473f https://open.spotify.com/playlist/0VTTnJgEPcBYWKddDZ7iwo?si=a20750b15e4f4246 https://open.spotify.com/playlist/2IBj89LQ0QR55Gf0HCbEyt?si=ff0a1f7e2832410e













"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
