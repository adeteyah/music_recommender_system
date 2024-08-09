import re

text = """


https://open.spotify.com/playlist/4atWdyMZcyh7bTkQFlB18Z?si=e1abb4afdb354599 https://open.spotify.com/playlist/5VwYIrOYiEH3NFGysW3KGK?si=3f7de4cf04d74445 https://open.spotify.com/playlist/7GLUzbIwVGzQncTELBnmE6?si=b7fbcaaaa707453a https://open.spotify.com/playlist/49tW4QpQgfUC4Ow8RNn6AK?si=26b51802111f43a5 https://open.spotify.com/playlist/6MjDPkNdY3HFMQZoUb6nHy?si=eaf31438d929417c https://open.spotify.com/playlist/23hD5D7bvXtkJGz2ni7s9e?si=89d2474a58cb49ab https://open.spotify.com/playlist/7CSZCwHqN9tJTZYq2hLxvV?si=0d3266c6cdbd4ec0 https://open.spotify.com/playlist/5CVVpqImw2ZqncmLScG1AJ https://open.spotify.com/playlist/2lNyFpXA18iMatCD7mSSrC https://open.spotify.com/playlist/6itrwpGEsghWagmPw5kvBA https://open.spotify.com/playlist/0P2yenFu8HJwjaJkbbTsZl https://open.spotify.com/playlist/00Ere1HIlf43WgPiwNGeyD?si=2e2a35cc595b449c https://open.spotify.com/playlist/2PPZudemIihxq4G9qEBUes?si=9b6316a38d1a4b85 https://open.spotify.com/playlist/3GYFonaP542KQjTDCdCZy9?si=9642abcbb7c549a3 https://open.spotify.com/playlist/12XTTMEKvujK7A2N6cnDUC?si=91dbf658e5184130 https://open.spotify.com/playlist/0OfGWwpaSBodw3GNUZmRFx?si=e5bf82949b53487b https://open.spotify.com/playlist/2w4xNqxLjGZ2YawfhWtz7c?si=2b3523fe70d146c8 https://open.spotify.com/playlist/2tdwwCnw8PPWjF5rN1I3SV?si=ade35a971848479c https://open.spotify.com/playlist/74xKnHheTTE89jPrZBzysC?si=ce829f032c384dbd https://open.spotify.com/playlist/46dTsij9Mu08aZEsBeprAt?si=6fb80261ec1c4695 https://open.spotify.com/playlist/1oAcJHS7reocJIpSe8TaDA?si=d217935639364a35 https://open.spotify.com/playlist/04LLNrUBAiqc4gXwzimfKL?si=afae1d2e35a347f5 https://open.spotify.com/playlist/1SRbwvLDJJhoxh0xvfT79e?si=71fec13858bc4e0a https://open.spotify.com/playlist/3FPU3c9G5v90G1G0Wvy5H2?si=440fdc168d864c9b https://open.spotify.com/playlist/0uxHbi3HPpLDOmZlf4KFu9?si=ebebc77295674300 https://open.spotify.com/playlist/4jZ18U8gUmPlg478f2qp6l?si=96e22fcb9dfe49b2 https://open.spotify.com/playlist/2b8pP4wcHYNKb7q9IIp6CJ?si=1f644c94c1634019





"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
