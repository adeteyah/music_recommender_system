import re

text = """


https://open.spotify.com/playlist/7DgPQwzEoUVfQYBiMLER9Z?si=09c53ca261624db6 https://open.spotify.com/playlist/1GXRoQWlxTNQiMNkOe7RqA?si=442c7d0dd152424d https://open.spotify.com/playlist/2XXdE3Nboq3b6KTuBU47Z2?si=0f937b6265494dc8 https://open.spotify.com/playlist/4nw4ZMYkoPoZu4HYdkN7VJ?si=d6f247d420764522 https://open.spotify.com/playlist/4QdDFN4F3GcHllBt2loOw3?si=9e33197d3fb94a78 https://open.spotify.com/playlist/5KcSmqijnFDyFTqDdr4QNz?si=4d1d66acdc944994 https://open.spotify.com/playlist/5KcSmqijnFDyFTqDdr4QNz?si=4d1d66acdc944994 https://open.spotify.com/playlist/3s0PAK76prh5be8UhW7sfD?go=1&sp_cid=faa19c672ecd66d2dbe5c4157fbbe0c2&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/27guQWIZg4kArVFff7BsjF https://open.spotify.com/playlist/50KJWq4mpnUwofCDysvreU https://open.spotify.com/playlist/0w5O7O6RVk479XrVyosLSH https://open.spotify.com/playlist/5cyDpvbfBQmLSJOQwTqWQk https://open.spotify.com/playlist/0tNebzSnS9Ypx4Jj0XuWjC https://open.spotify.com/playlist/2aE3crv7lrl4VMdsR7g8Oz https://open.spotify.com/playlist/5NWD2pOGBYtcOG4kvHM4fu?autoplay=true https://open.spotify.com/playlist/04rREDiHtruOKqq4zSl4H8 https://open.spotify.com/playlist/13CGS5YwiFvMyK3nhV65zH



"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
