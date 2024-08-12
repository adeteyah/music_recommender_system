import re

text = """
https://open.spotify.com/playlist/2MYnGyPrRVCbVfDhxtaTbz?si=2cee1bc1d2e44207 https://open.spotify.com/playlist/29C4QuiH7GdGaaskykqPFE?si=5d897bc24c504960 https://open.spotify.com/playlist/5qSmvjITVRNAcSRBCa2tJ9?si=591c5e46d0014a85 https://open.spotify.com/playlist/6O6YHgNv2mPHJrNFhuJFHA?si=c88acaee9dea4c1c https://open.spotify.com/playlist/0Yah2D11WPmTuONCPpF3qn?si=2e38b8481ce04fa6 https://open.spotify.com/playlist/3yiG6XhN5ICyHfDIN1nEwf?si=a065d3d7bfbb41fc https://open.spotify.com/playlist/7xlEcKmVmyOeqfWFEdQByy?si=ef96cf25c6b14343 https://open.spotify.com/playlist/3pjX9hIfm02pzlA06OChAC?si=6591c65a71a24299 https://open.spotify.com/playlist/3mBSlfof9pREMuy3n8JBIA?si=118760a6745f4b25 https://open.spotify.com/playlist/3OFXagnf7vaDvTEwhzv028?si=6c84943064c348a1 https://open.spotify.com/playlist/23nwOAo3d6keYotcwiMqoq?si=22599c5471224056









"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
