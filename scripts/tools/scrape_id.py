import re

text = """
https://open.spotify.com/playlist/0dXFgLEEjRr9t8Wa10xEog https://open.spotify.com/playlist/5WqHfJDRG5Gmyw65LR8Uqo https://open.spotify.com/playlist/39tv8YyHEVv3KahBgnFgu0 https://open.spotify.com/playlist/1vAMUOtqw8QpsoBUZdflxU https://open.spotify.com/playlist/1ucG6SKrmHR2AErk2jMg0I https://open.spotify.com/playlist/5gos3UzDEqKzFwhHckA3n3



"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
