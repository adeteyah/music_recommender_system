import re

text = """


https://open.spotify.com/playlist/7DgPQwzEoUVfQYBiMLER9Z?si=09c53ca261624db6 https://open.spotify.com/playlist/1GXRoQWlxTNQiMNkOe7RqA?si=442c7d0dd152424d https://open.spotify.com/playlist/2XXdE3Nboq3b6KTuBU47Z2?si=0f937b6265494dc8 https://open.spotify.com/playlist/4nw4ZMYkoPoZu4HYdkN7VJ?si=d6f247d420764522 https://open.spotify.com/playlist/4QdDFN4F3GcHllBt2loOw3?si=9e33197d3fb94a78 https://open.spotify.com/playlist/5KcSmqijnFDyFTqDdr4QNz?si=4d1d66acdc944994 https://open.spotify.com/playlist/5KcSmqijnFDyFTqDdr4QNz?si=4d1d66acdc944994 https://open.spotify.com/playlist/3s0PAK76prh5be8UhW7sfD?go=1&sp_cid=faa19c672ecd66d2dbe5c4157fbbe0c2&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/27guQWIZg4kArVFff7BsjF https://open.spotify.com/playlist/50KJWq4mpnUwofCDysvreU https://open.spotify.com/playlist/0w5O7O6RVk479XrVyosLSH https://open.spotify.com/playlist/5cyDpvbfBQmLSJOQwTqWQk https://open.spotify.com/playlist/0tNebzSnS9Ypx4Jj0XuWjC https://open.spotify.com/playlist/2aE3crv7lrl4VMdsR7g8Oz https://open.spotify.com/playlist/5NWD2pOGBYtcOG4kvHM4fu?autoplay=true https://open.spotify.com/playlist/04rREDiHtruOKqq4zSl4H8 https://open.spotify.com/playlist/13CGS5YwiFvMyK3nhV65zH
https://open.spotify.com/playlist/0NvvaMiyRetzt9jupbFYNM https://open.spotify.com/playlist/4LWEtQg7bluwJdCFMkJ5MU https://open.spotify.com/playlist/5DbG43JvL8S5AqUBMcbNYI https://open.spotify.com/playlist/0nZsRUSK2l9knzLuEySw8I https://open.spotify.com/playlist/1Fcg7hNoJ5LtwYM8yOPDYm https://open.spotify.com/playlist/3a0h2rnDAboudVYu6aqgRo https://open.spotify.com/playlist/2DW2OSfjGOWLEDnV0vfyoH https://open.spotify.com/playlist/0SjD3C9qWCzmo1KafmUGjM?si=fcb6057c2c5d4cf1 https://open.spotify.com/playlist/50nNxCc7ZB7CUK1skmwHg0 https://open.spotify.com/playlist/7EZHWvnmRstApKcNkPsFv9 https://open.spotify.com/playlist/1ZliBwZNuYLnMkfQJVGGLe https://open.spotify.com/playlist/7nAeJJEjmovQMp5rPDhchd https://open.spotify.com/playlist/2DxMYnLncCqgEryVVn0cQ7 https://open.spotify.com/playlist/63LbOL6wnQilTuBhsLIuF8 https://open.spotify.com/playlist/5w15kmo03vurAm8g2wT34c https://open.spotify.com/playlist/1LoaUK8r21Wfn8dlw7j6OZ https://open.spotify.com/playlist/1DLZTD5ANcNBQy8AFUGMOt https://open.spotify.com/playlist/5ildE24iDDIhyfkavBvoYp https://open.spotify.com/playlist/3Q5I41rLqz3EwYODPMUFXr https://open.spotify.com/playlist/2B0MOFCoaOOeHU1hy7OOWq https://open.spotify.com/playlist/4UBNUes6dhYGWQr2k8Ltfo https://open.spotify.com/playlist/0PVaskCvkHqB44COOb4xUe https://open.spotify.com/playlist/5KVjiEr9v2Qy0kuD6227cz https://open.spotify.com/playlist/3Gd025NKDIZQuT9aj0PTbL https://open.spotify.com/playlist/2PtWsAccOJBzNcjXGOjo06 https://open.spotify.com/playlist/61WkMGqjhLKOgvMwfXc8tS?si=b85087750b864fc4 https://open.spotify.com/playlist/6tUoLGh3ueIMVoYbBVZpKQ


"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
