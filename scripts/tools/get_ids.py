import re

text = """
https://open.spotify.com/playlist/4HR8Y0emDAiE1wM3XILoZP?si=f699ae306e084231  https://open.spotify.com/playlist/5KgQT9YWz3EqhIN4Jh69IU?si=1dbc1a66fe924bbb https://open.spotify.com/playlist/0PtjYd3OYwJ6CvzdLJVoP9?si=6631554bbead4a9d https://open.spotify.com/playlist/4qiS6MsylP3SQhfAre2O9g?si=f2cd31494cf949a4 https://open.spotify.com/playlist/7k30DQOSdd8qIQbhsxzsxV?si=9a7860f6cc7b4f23 https://open.spotify.com/playlist/0RxrVAVY0Bz067UajBMYPS?si=d4a76702455a4728 https://open.spotify.com/playlist/73n5eYkmp0xA46hPXg4AJ5?si=11011d44732f4907 https://open.spotify.com/playlist/6h8B6q9PumfbQFf6gJ2zqI?si=4df1e0814c7b478f https://open.spotify.com/playlist/08VwBRNVGPcF0vT5uKAHtT?si=361efc0c8aac4f9d https://open.spotify.com/playlist/3l5y0IdNtMYFf4YEqQjWj2?si=752c279895424bf1 https://open.spotify.com/playlist/49i2nsUghVlzKOnNJtzhkJ?si=348b718d9323403a https://open.spotify.com/playlist/4wkCgQR6AQ3F1yKfXsVfo6?si=3f7d5457c4b046eb https://open.spotify.com/playlist/4ShulrGSaVc6ZvbLzuegYK?si=5d854845043f40c9 https://open.spotify.com/playlist/6bd0a0UHF8wGthySFrxRFg?si=b397d265e24841ca
"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
