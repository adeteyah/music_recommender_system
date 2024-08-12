import re

text = """
https://open.spotify.com/playlist/0qbMhlJCuyQrjQQ8RW2yQp https://open.spotify.com/playlist/4hlICq8ApjDdbCGtNOVJ9J https://open.spotify.com/playlist/3RUvmYSEo3BMxIT7jk5Z8a https://open.spotify.com/playlist/2H99P17etjoiFCVBm5CXLI?autoplay=true https://open.spotify.com/playlist/691vgok4JnJzVRFDiDzH9l














"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
