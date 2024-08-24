import re

text = """
https://open.spotify.com/playlist/0EgvlxC5C55kfhAp3z8XiQ?si=da5361cd1cbe4779 https://open.spotify.com/playlist/2boNrskD7J0V1hm8zWuUQm https://open.spotify.com/playlist/7aeD2DfaAZVlcv2mqsv2Af
https://open.spotify.com/playlist/4dzEvKgheWpwKvEkeYRWJ5  https://open.spotify.com/playlist/672YsqAt3WjQM6WCmgVZFH https://open.spotify.com/playlist/5lQ7n4NXqhYNCeMzYEfWBj https://open.spotify.com/playlist/5jACHXLmCPidvkn1hzG3GH https://open.spotify.com/playlist/29icOD2MBCTM3X1KMx58uD
https://open.spotify.com/playlist/6hULLeAMSplOTqmzjpi5pc https://open.spotify.com/playlist/4GugtOrcyVCJfrCByTphob?utm_source=spotify_crm&utm_medium=2017q4&utm_campaign=2017q4_global_global_alwayson_free_onboarding_2make_playlist&gtm=1&fo=1 https://open.spotify.com/playlist/37i9dQZF1E4wpSCb6QF62a









"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
