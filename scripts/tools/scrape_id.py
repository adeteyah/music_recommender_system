import re

text = """


https://open.spotify.com/playlist/7sMerhMCG0DGLTHJg3wxnx?si=1d7f5dd4e1f14cad https://open.spotify.com/playlist/37i9dQZF1EIfEvNEw1FAvr?si=43eb2b65eb354c3f https://open.spotify.com/playlist/1Mu6QdrIEk9bNkk1bBW4X0?si=24bb41afa1c84fb0 https://open.spotify.com/playlist/64e4GpdJUJdOxy9pfXlTJ0?si=f12a7231f5c24941 https://open.spotify.com/playlist/1a7oOOBs9p9ib50SHd6nWf?si=b268919d91e443ce https://open.spotify.com/playlist/0uHJpG7IDUf7JIfsRIKWeq?si=3feecaaa7d8a4d05 https://open.spotify.com/playlist/2xz5sr95lUcqFnRr1gWeYc?si=f5b135efeef34809 https://open.spotify.com/playlist/1iD4oLyiTH1w1B9neIrxtN?si=d6877a85261f4560











"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
