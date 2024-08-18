import re

text = """
https://open.spotify.com/playlist/5wSBFp5we0nqorbGqZASqK https://open.spotify.com/playlist/7zdIx8XsuMRkdgdPPLK7v0 https://open.spotify.com/playlist/3fhS7CqKhmKUveyyL5WVwK https://open.spotify.com/playlist/7pLAxk3MNdDYUyPXQqQxP7 https://open.spotify.com/playlist/0AsSCRRNGrhaVawrTl3yxs https://open.spotify.com/playlist/43YtzQ6raCES8vURyTB46L https://open.spotify.com/playlist/36agJJVP1XSZY02xzwE1uP https://open.spotify.com/playlist/31ohmMTmsmwCWS7TPZOsc7 https://open.spotify.com/playlist/6mb9G1ApPjcFWmml8KTK2x https://open.spotify.com/playlist/7i6Hg2nwGlLVJEgRcGAROh https://open.spotify.com/playlist/3tSAGTHlBRzns3T4OaUeIZ https://open.spotify.com/playlist/30q3yIoYtZ6WTIyJ94Bc7A





"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
