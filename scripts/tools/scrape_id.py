import re

text = """
https://open.spotify.com/playlist/0j4j50lLJrYSe9O32fAhTf?si=e5b8ba833eab4995 https://open.spotify.com/playlist/3GSbVK2oQb5CDOmT1Bx8Im?si=eac6fe530bc8467a https://open.spotify.com/playlist/3yTZhSfCOgmI2giuXPkwRM?si=5af72c925e304782 https://open.spotify.com/playlist/1Vu3f6W8ee1CcnwGnEDZGB?si=3db7dd5552e04219 https://open.spotify.com/playlist/5VGchw4RXeoziGcjKifKPH https://open.spotify.com/playlist/54sUacKOrS70xNuQo8G9yJ https://open.spotify.com/playlist/1aaFNqRlEz6bVBpW9PaVHz https://open.spotify.com/playlist/6O4kgn1uSndPTw6gM6rUbL https://open.spotify.com/playlist/20uDlGeKhK2idqWDlcxUh7 https://open.spotify.com/playlist/122fTm8g302syPXqs4MTvP https://open.spotify.com/playlist/0jt8TNZFXiKmmOhaGjciym https://open.spotify.com/playlist/70GSgNtGcetyd626vzglmj https://open.spotify.com/playlist/3MyrklawQNDgK0YIIHuUFk https://open.spotify.com/playlist/1N1oe64WtqKOrHKhfRuNHS






"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
