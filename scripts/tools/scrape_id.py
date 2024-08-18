import re

text = """
https://open.spotify.com/playlist/2dHb0aB8IQEDTxqymWqvfE https://open.spotify.com/playlist/4ldNqfCjP1cFbULSkv2tfb https://open.spotify.com/playlist/3M7RT85xu5DQ4MjXp7D8CA https://open.spotify.com/playlist/5pRm1Urao5hO6YNcIxvVZX https://open.spotify.com/playlist/0zPbEMxveRMhnFxc9MqaDn https://open.spotify.com/playlist/1iCzA0f7Prp6C9ap5mRYvt https://open.spotify.com/playlist/5wYznTRPm4DPiWasExVN5p  https://open.spotify.com/playlist/1wH2w17ULzCMqHh4T8PIa0 https://open.spotify.com/playlist/51HBHUPs5qowNxm0WCd3hO  https://open.spotify.com/playlist/5Ph7YD116r7cWdJBEPY0TI https://open.spotify.com/playlist/4whrH8VBkbHSfOYRK4i7i0 https://open.spotify.com/playlist/4whrH8VBkbHSfOYRK4i7i0 https://open.spotify.com/playlist/5tM9Ivg3zq0GTYddDiqfkU https://open.spotify.com/playlist/6QDNdalbzdN45kyHx4upLM https://open.spotify.com/playlist/3oqNWDNayfTg8LkVl0oDFB https://open.spotify.com/playlist/37i9dQZF1DXbEm2sKzgoJ8 https://open.spotify.com/playlist/7EzOz99Q8ydRsQSnkPUHCK?si=lKcwsTqsSjSFEQH_DAbcEw&pi=u-9kd7hr5fRYOB https://open.spotify.com/playlist/5PAUOGIn9owQHQIVSO5UJC https://open.spotify.com/playlist/5zeiXWuSLl4tVhJ1KO1RoY https://open.spotify.com/playlist/71G9jK3syzeqiRt77ihxJ0 https://open.spotify.com/playlist/7xhNTdxImpSdV1aGsNLlOn https://open.spotify.com/playlist/4WVLVRAdEEPY0EwcK32XMp https://open.spotify.com/playlist/1OUPDUQABebnhzCAKGHXTw https://open.spotify.com/playlist/37i9dQZF1DX3ORvAIr1RbU https://open.spotify.com/playlist/6BBChmyEHeCcx1gdcfG77H https://open.spotify.com/playlist/5TQ9IymI6oFG9Gm0YiTQi9 https://open.spotify.com/playlist/62KGJKfY57DriYRePa97gC https://open.spotify.com/playlist/2SVKEnKxbwdG8GqeWi1g6w https://open.spotify.com/playlist/2IlNa6S6Nqd9NfQfJ0DECL?si=1Iq6MJsRTCWJVRIMhZidww https://open.spotify.com/playlist/37i9dQZF1DWXBcLLksEQAf https://open.spotify.com/playlist/0YQ3cd7KqFSDtczetJqvyG
















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
