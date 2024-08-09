import re

text = """
https://open.spotify.com/playlist/7561pRhGID1JY9iylnjTeC?si=01162454632345ef  https://open.spotify.com/playlist/5FIczQXxvrVuqiLT8zIw5f?si=a4c6aece05e9491a https://open.spotify.com/playlist/49Jw0JbNJexKQGo9KpPGsO?si=765b3abf853e48c2 https://open.spotify.com/playlist/0EWoCeUOQAEEIVmIkfpMP2?si=94d4839e50264d07 https://open.spotify.com/playlist/0SgyK6Rl58KJH3UGWDhSyc?si=a3a2237b16924a37 https://open.spotify.com/playlist/6uLsdWljLVNjLuPRlehDt4?si=92e0bec200c44dab https://open.spotify.com/playlist/3t9g0zGUYvn91KlEYeg8CN?si=688c3a172bf5409f https://open.spotify.com/playlist/1BJjVFVmV6kdXDZZpwaxSK?si=eea87ab202094277 https://open.spotify.com/playlist/3AUAs41Vr5wcwbGHq9ksHH?si=dd4d58e50ef94b19 https://open.spotify.com/playlist/49Ek1T3Hlr3Znwx8qHHg5g?si=a3690838cc794fb8 https://open.spotify.com/playlist/0SgyK6Rl58KJH3UGWDhSyc?si=297a40a0d47f479d












"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
