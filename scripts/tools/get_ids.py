import re

text = """
https://open.spotify.com/playlist/4wd6242y2qn44TiCCPX12W?si=1b110b8722bd47c1 https://open.spotify.com/playlist/1px2X8PZWU2DYEKguX9MnO?si=213c0591cbf3446c https://open.spotify.com/playlist/01MRi9jFGeSEEttKOk7VgR?si=4d00458f41274418 https://open.spotify.com/playlist/7CUk41Loxfzf7COHvGAFgC?si=13ff3eae4cc9444a https://open.spotify.com/playlist/7EnIitpBIDp8hbqoaOWfQO?si=b11b39eca1584f5e https://open.spotify.com/playlist/79Fcztgis2C4fuFXOv1z1A?si=ffe25d4067e14247 https://open.spotify.com/playlist/4dOrHR4M1VfJw95k5z44xK?si=4e148ae8ce1f442d https://open.spotify.com/playlist/5mT9nfLXxLHNTCd4gAaxkH?si=94a8833faf1043b3 https://open.spotify.com/playlist/6v87Ys6VCgwpZ7Yc1h6r0N?si=0adcfc0d62c347b0 https://open.spotify.com/playlist/4nMkjATDqJu3j3LHSt3g31?si=ece94044aefe44c4 https://open.spotify.com/playlist/05ObK2w1GdACIgvlxTHpII?si=ee2ca50c335e4da4 https://open.spotify.com/playlist/7wV4guZMZNGnvNobXKdJea?si=cad6af7b68fb4d80 https://open.spotify.com/playlist/1Zsr1Qv5Gy41vVKVWeRAs3?si=5a50580ae09247e7 https://open.spotify.com/playlist/6tRJKsTY9vyEmlNqSx9D7k?si=f537ae0072f44fa8 https://open.spotify.com/playlist/6i4EhDZQivCT9MGsydRTy5?si=85836e8826f84427 https://open.spotify.com/playlist/4ur3EQ99u2W5MOS3DXd6LG?si=6905b3a364384394 https://open.spotify.com/playlist/1BAPmljFQSOQGH0EFYqAbP?si=c29ce2d9ed514c15 https://open.spotify.com/playlist/06ZLNy6cTjQiixGwSwgpVC?si=fe1e366996344304










"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
