import re

text = """
https://open.spotify.com/playlist/5hOH3HcnQon0lWreL9Tfwx?si=1831a60baeb145ce https://open.spotify.com/playlist/3BnhVf03cMI7vvJnbaVcpv?si=97a1c22357b04675 https://open.spotify.com/playlist/2jGJ6mtKuMBqIZsC2A8WYU?si=7c9b95c0c6bb4b27 https://open.spotify.com/playlist/0W4Becbl7WgXre2YuQlF6Q?si=270a2bcdeee34515 https://open.spotify.com/playlist/7ioNIqTcZfMCF6a730PZXS?si=58cb9e72925248a9





"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
