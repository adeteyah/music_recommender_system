import re

text = """
https://open.spotify.com/playlist/0GLSdZe76S4SBKVl9x83ZO https://open.spotify.com/playlist/2vjpPSXTglRqmHH9IZkqJ1 https://open.spotify.com/playlist/1Mzt5wkZyqfwDvAU1gXkr8 https://open.spotify.com/playlist/6j2w0ULVWUfQBZRWjD7rk8 https://open.spotify.com/playlist/3dWqdXeol8puL98GMFcQqe https://open.spotify.com/playlist/1yB5Q9nAjfq9AhuqcTeHJQ https://open.spotify.com/playlist/6F35fnYjUyzovzMMqxCLsu https://open.spotify.com/playlist/2rHcNhaUb22E7KLgVr7PHS https://open.spotify.com/playlist/6xStG8FiEZis35y3yUvqkf https://open.spotify.com/playlist/0dtQfgq9LaKWuxIe4FgSqo https://open.spotify.com/playlist/172kFhE7gxJj0qtefxFtW4 https://open.spotify.com/playlist/3IJPxtfrdhQFQzT7C7OeQt https://open.spotify.com/playlist/4Ss25odH5BIlDrHCIpu3Fj https://open.spotify.com/playlist/31ydy98aMJanuw2QCwZkZ2 https://open.spotify.com/playlist/6osq2qEHwHmQQPtpXb9V5W https://open.spotify.com/playlist/2Sew1y4M1xV5dlvYjM4uua https://open.spotify.com/playlist/3wdQHU1ibDWykzgXhznFey


"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
