import re

text = """
https://open.spotify.com/playlist/4HO09Zco5iBfgE7UKhOPoc?si=d17c6be0776d4a39 https://open.spotify.com/playlist/40D0k2BclPUm4GqU1BTik6?si=64945e0c76024ce2 https://open.spotify.com/playlist/1u2evn7kaunEEFykRfd9r3?si=da6a0d73891149c2 https://open.spotify.com/playlist/5T6JdYxZaXZfW55zJtTHWU?si=aff3b61d77f84b74




"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
