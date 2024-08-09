import re

text = """
https://open.spotify.com/playlist/5PoSBkMZayOGwSsqd0eFfh https://open.spotify.com/playlist/5nFFSzOiBIhZIMeT4G8cRA?si=aba3085728f1410a https://open.spotify.com/playlist/7GWUkxZPIep6ldxFeZDBzv?si=e73416d34ee24a8c https://open.spotify.com/playlist/4qskHJgbhpK6PlAwJ827ZX?si=e064981f43484234 https://open.spotify.com/playlist/53PjvXmJwR9f1PyeQJjbTq?si=c51816ceb988404e https://open.spotify.com/playlist/3jdDGwd346YV0EEzogVa4S?si=df726f97307343b1 https://open.spotify.com/playlist/2EoheVFjqIxgJMb8VnDRtZ?si=04cd9134b70b4ab5 https://open.spotify.com/playlist/5V5dFZI713NfATCULuZNUE?si=258b24e663034f27 https://open.spotify.com/playlist/4baOzx2YK9GySzMNDLVWUo?si=581ed6aef60747e1 https://open.spotify.com/playlist/3Ir5YWemOTGRRfXgROrsDV?si=235d2784f7d64ff2 https://open.spotify.com/playlist/0S2dMUap6RL4C1lv0IntzT?si=b0055feba9474522 https://open.spotify.com/playlist/0M5ovmRC1KXlHCEf91t2Zj?si=ae3a474348b44124 https://open.spotify.com/playlist/208oh1YKszRsSW7Jf3jfcC?si=1d76a7226b9e4019 https://open.spotify.com/playlist/6Z05FMYGnZxTzxU9AZRsWA?si=64522b56ed43497c https://open.spotify.com/playlist/4fYgp8att0vhdRWZoTUUWu?si=51626796035b4705 https://open.spotify.com/playlist/71BHBFtI7gkR7LuUwpDXM9?si=3e82f733895744ce https://open.spotify.com/playlist/1vjcIxatKz6794oJOZlegn?si=2496b86596a3454e https://open.spotify.com/playlist/0NVIRzGi5tF0fz7F7uqtRe?si=f91fc0c4d7fe4189










"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
