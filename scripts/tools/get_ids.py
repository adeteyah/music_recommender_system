import re

text = """


https://open.spotify.com/playlist/3ErsNWUyTyfBk5BKVbQqwA https://open.spotify.com/playlist/4fEjH3Z4EnUrm3A15NSpVG?autoplay=true https://open.spotify.com/playlist/0CvTWPI2RU7sDdTu7Jzo0f https://open.spotify.com/playlist/31JKnp3rdqohPdMTKn9XbH https://open.spotify.com/playlist/0kWTePaZRjxsiz71iwJ4Vv https://open.spotify.com/playlist/5WB11JYS6bhctRKjaTAzbE https://open.spotify.com/playlist/33IjV5YQSVQ1iP5ZWPoed1 https://open.spotify.com/playlist/0RN6NWzxFc0yYC3zjqUTyv https://open.spotify.com/playlist/0EuzoglUoehtp7RtQD0b5t https://open.spotify.com/playlist/0yP7gvpTYoXyophp0v6YAA https://open.spotify.com/playlist/6HdV5wQbP4PDtenT9QrYqe https://open.spotify.com/playlist/0WglLmBpbqJwVcAgNVdrug https://open.spotify.com/playlist/6xNm9Hy6Ov3XRp35HqX0jB https://open.spotify.com/playlist/50pPomwv9lXyn2BvyqU8j4 https://open.spotify.com/playlist/2g51E0903QstXhoqlKZa8o https://open.spotify.com/playlist/5gpLw8LTykzVrZKqruNsr0 https://open.spotify.com/playlist/5czT0ZivolWNkyZsrSUygE https://open.spotify.com/playlist/3t1QJ0Uz80V5ZvxBbcplyx?si=DoCS1qMfSd-36HIGXhX6Jw&nd=1&dlsi=7e7773a43873495f https://open.spotify.com/playlist/5Va2lzU3EmcphyPLzVWAw8 https://open.spotify.com/playlist/7L24WWy5FCuDYJtJokkojm https://open.spotify.com/playlist/3jT88Q3c7J1e2ir0LGlTPh https://open.spotify.com/playlist/3Imzqjg5cu6ckkO579CmwK https://open.spotify.com/playlist/5kr0QYISRNbVjl7eKuVnIu https://open.spotify.com/playlist/7pa5trRubojsazci1tufjE https://open.spotify.com/playlist/43Spff9IB9KE5XlySFbDze https://open.spotify.com/playlist/76rIQMBILwrXAQaRLEclot?go=1&sp_cid=15c3875ea74156c21cc717472b4a74da&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/6o6OluyTfi5zSi32aUyXYe https://open.spotify.com/playlist/2UirNtiVbtV10OTQaJcwt8 https://open.spotify.com/playlist/0PA4LSXxbw9F4h40d3Ds4i https://open.spotify.com/playlist/5ai46ln7Rf0yNL0aEueRwp https://open.spotify.com/playlist/5OENPv3L1CfACN6IvCuxw0 https://open.spotify.com/playlist/0XX7HjholjzFLPIUdFM6h0 https://open.spotify.com/playlist/6jRUOMR1vLimHOoWp18M9E https://open.spotify.com/playlist/6cMMb9ERhyLixnx6mwpj7l https://open.spotify.com/playlist/2R6VWqGMnJF1JMdKmMFS11 https://open.spotify.com/playlist/2Lo6g2yZU0fKCWbGiqdoW2








"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
