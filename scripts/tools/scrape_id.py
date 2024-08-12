import re

text = """
https://open.spotify.com/playlist/5cFrQhNIs6lKx9blqDUaJq?si=d30ad11b74ce4f09 https://open.spotify.com/playlist/4UpTqgnSsnw82doYIRcemf?si=6e569334680b480b https://open.spotify.com/playlist/4wGjy2qOerJAo4uJVploUO?si=fd25a852ffeb4639 https://open.spotify.com/playlist/2b8pP4wcHYNKb7q9IIp6CJ?si=4a100181ad11400c https://open.spotify.com/playlist/2PPZudemIihxq4G9qEBUes?si=21b02e7d037846b0 https://open.spotify.com/playlist/4V4yDbBaR1zT5NKCcXS00B?si=000da640c90e4e5d https://open.spotify.com/playlist/0ifxAMSsops4pP036J61WZ?si=8a98a30eea044044







"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
