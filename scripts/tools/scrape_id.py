import re

text = """
https://open.spotify.com/playlist/01Tfrx2qWhWWeaDdAq33bb https://open.spotify.com/playlist/6Y8v3uYevXV2Lxs33dOUBX https://open.spotify.com/playlist/6vtwdVS7vAu04wHvcKfrZF https://open.spotify.com/playlist/02Zp5SVMdsb90w8IrSRV6g https://open.spotify.com/playlist/18TBQDIUeUvNsoUyNXZt4y?autoplay=true https://open.spotify.com/playlist/6Y8v3uYevXV2Lxs33dOUBX














"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
