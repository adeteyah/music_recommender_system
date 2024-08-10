import re

text = """

https://open.spotify.com/playlist/64L6MntymuqQRuif9nVM6c?si=b635334cf51f47fd https://open.spotify.com/playlist/4x9Id1MUfg681SR5tR40vV?si=c680e3deec1341e7 https://open.spotify.com/playlist/3DtdtaTZfZPNEqttZ2vVG0?si=fd2fff376d21433f https://open.spotify.com/playlist/7vq57TiBTpm5IMfiWs5PBh?si=c2f7c922fea04eff https://open.spotify.com/playlist/1Uon4YjxrFKECs3cxuq0s7?si=d939d5e5693e4b7b https://open.spotify.com/playlist/4BFbPoGAwZsEJJKW7c0IUF?si=b91b02d821864107 https://open.spotify.com/playlist/6vBkuOkhUAu77sBYdMAVDJ?si=4bc687f3d2844335 https://open.spotify.com/playlist/5xl6pngUNTpJkMEcgq70an?si=37603c3a505e415c https://open.spotify.com/playlist/4yNUxofGRcnw7UknxONOYC?si=7f6f81a5e9bb46d0 https://open.spotify.com/playlist/2S9qc8q5xU9M9HtLWKHFRJ?si=4396dfe6d124479c https://open.spotify.com/playlist/5reCpCSw8NgB5QjGILvrhX?si=4ab51e6f49ce4054 https://open.spotify.com/playlist/2JsYYV1eTQsHjznasUIaru?si=3aae90827d8f4217 https://open.spotify.com/playlist/3iuP5ovrQcGkfRtLk11zau?si=2f0c50d888f54e2c https://open.spotify.com/playlist/6mqJU05sWmXTuY1iO1RXmK?si=64ac0d01d3ee472a https://open.spotify.com/playlist/70mJkUkq5bIP6w6BI25cov?si=b01a548de2f84cef https://open.spotify.com/playlist/15NJtngbNqxyN47NV7ssXJ?si=35167c1f8200427b https://open.spotify.com/playlist/1YXxGeLWtd8qeHJTc6zW6u?si=67fce9682bed4999 https://open.spotify.com/playlist/29xqS54FRT6qeWDXnYLwOE?si=b49f812622e34185 https://open.spotify.com/playlist/7E8T698a0KyfUuXyE5Wrve?si=237ff01cfdad4c94

















"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
