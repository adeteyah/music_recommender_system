import re

text = """



"""

user_pattern = re.compile(r"https://open\.spotify\.com/user/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
