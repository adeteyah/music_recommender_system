import re

text = """
https://open.spotify.com/playlist/37i9dQZF1DZ06evO4s4B1e https://open.spotify.com/playlist/2FnzHLgRojDJSQCmMwOy0O https://open.spotify.com/playlist/17mIXPwdLS4piVL3OzSirt

https://open.spotify.com/playlist/5lubzlfVf4fnCyhDtGiVtC?si=c9740e47ad894e35






"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
