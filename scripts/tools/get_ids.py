import re

text = """
https://open.spotify.com/playlist/7AymJjcD9CtBdMC4ZUuged  https://open.spotify.com/playlist/32ekZ7VXPoIHR7FCNiVECb https://open.spotify.com/playlist/30dp1rWpmhVWEZlkfuqXDv https://open.spotify.com/playlist/1YLFtO5vLHVLYt4i4wsOkx https://open.spotify.com/playlist/15ToYP7ia1JWHSfKwW68to https://open.spotify.com/playlist/2yeKkjKNOdzjIZ2f1Gt6X7 https://open.spotify.com/playlist/69IO1ED0vH69LI7Vl9ZrrN https://open.spotify.com/playlist/37i9dQZF1E4xGmYXXidXaI https://open.spotify.com/playlist/1mIWX9oxhMxd2heXLJsrfA?utm_content=buffer9e0b8&u=&_php=1 https://open.spotify.com/playlist/091MAEH2NKjAQZ9r4SspDs https://open.spotify.com/playlist/637J6DekptsyQe2q2OK3m2 https://open.spotify.com/playlist/4XAmKNfoyCGNt9Z7zTAOmJ https://open.spotify.com/playlist/2jpPcsDR7qb9xgGF1DyGoU https://open.spotify.com/playlist/0DrkxNbmDUz43nIUkMQnEO https://open.spotify.com/playlist/5ijJgOVBwjzHec1Jgexu4t https://open.spotify.com/playlist/3tOHJZkUC4LtqQbREhuDDG https://open.spotify.com/playlist/34N0gsSTrlGM2Hx83f9l1k https://open.spotify.com/playlist/39tv8YyHEVv3KahBgnFgu0 https://open.spotify.com/playlist/55M6sFoow7KjS9tz0CSZxw https://open.spotify.com/playlist/4KfO6J8jj2Jqjlq9YaVyzm https://open.spotify.com/playlist/0dXFgLEEjRr9t8Wa10xEog https://open.spotify.com/playlist/5gos3UzDEqKzFwhHckA3n3












"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
