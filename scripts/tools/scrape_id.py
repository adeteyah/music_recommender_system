import re

text = """

https://open.spotify.com/playlist/0yEJHHdRIIWceGp0Rt1JT1?play=true&utm_source=open.spotify.com&utm_medium=open&fb_action_ids=685153528199177%2C685151228199407%2C685151014866095%2C685146524866544&fb_action_types=music.listens&fb_source=other_multiline&action_object_map=%5B10150394495675341%2C10150280119582801%2C10150168325958601%2C10151124840875501%5D&action_type_map=%5B%22music.listens%22%2C%22music.listens%22%2C%22music.listens%22%2C%22music.listens%22%5D&action_ref_map=%5B%5D
https://open.spotify.com/playlist/2yIJO3lKN5h3lbayRXXm38?utm_content=buffer9e0b8&u=  https://open.spotify.com/playlist/5vSGXhW33I9KFtKTslVdzg https://open.spotify.com/playlist/6jeJcuvFUVEo3JXYA49gms https://open.spotify.com/playlist/64FkxTLLTbbPG3B0AAsErs https://open.spotify.com/playlist/6QtUzZuHzFPxUcIo1U8lSh https://open.spotify.com/playlist/3NraeakOx8Ms5x3LDekFFk https://open.spotify.com/playlist/1EXiX8R5G6H2XHDy37Ufdj https://open.spotify.com/playlist/4nnhWjcavAqdFGHkRrxPuX https://open.spotify.com/playlist/4aIG2sbsxzAoKRCLrKx6x4 https://open.spotify.com/playlist/2pX1fAX4EkSb14SPHAZndB https://open.spotify.com/playlist/5plMEplzpwP6iUJjYOsVqv https://open.spotify.com/playlist/6cB00x9bpjzbIWua0Nt58l



"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
