import re

text = """


https://open.spotify.com/playlist/7sMerhMCG0DGLTHJg3wxnx?si=1d7f5dd4e1f14cad https://open.spotify.com/playlist/37i9dQZF1EIfEvNEw1FAvr?si=43eb2b65eb354c3f https://open.spotify.com/playlist/1Mu6QdrIEk9bNkk1bBW4X0?si=24bb41afa1c84fb0 https://open.spotify.com/playlist/64e4GpdJUJdOxy9pfXlTJ0?si=f12a7231f5c24941 https://open.spotify.com/playlist/1a7oOOBs9p9ib50SHd6nWf?si=b268919d91e443ce https://open.spotify.com/playlist/0uHJpG7IDUf7JIfsRIKWeq?si=3feecaaa7d8a4d05 https://open.spotify.com/playlist/2xz5sr95lUcqFnRr1gWeYc?si=f5b135efeef34809 https://open.spotify.com/playlist/1iD4oLyiTH1w1B9neIrxtN?si=d6877a85261f4560 https://open.spotify.com/playlist/2IZvQ43MXV6TrwMy4TWirt?si=56c2ae4631c74dc3 https://open.spotify.com/playlist/7pAeOmjIkPcIZkxfgGN8sT?si=3c6c7941ba5a42ac https://open.spotify.com/playlist/6AACbfnDjOKf21e1RSJpvW?si=cbd91d35f80f4a61 https://open.spotify.com/playlist/0FCatX58mfH9ELGIAoPF7g?si=f826f2bb82184c62 https://open.spotify.com/playlist/0wgSBwjwNynF5hIysOBYDe?si=ab3f2f30dd094483 https://open.spotify.com/playlist/2WvUOkJZZRBofeMQzIpPwt?si=1d13bbb5d02e4b7a https://open.spotify.com/playlist/76FgbOAhbGGDYNXRci2iS9?si=f31fd6f42ee84951











"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
