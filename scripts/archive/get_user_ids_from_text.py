import re

text = """
https://open.spotify.com/user/31xyna5wagkylrcwc6wiio4tu5ji?si=7842a7ee7c68473ahttps://open.spotify.com/user/88qhmnsnyewlgfh4reytf1bqo?si=d0df882eba58428dhttps://open.spotify.com/user/12162238821?si=c84114b20569488fhttps://open.spotify.com/user/piwz3bc0dmv9z1wduk24z2nn7?si=6359f9eaf54d4509https://open.spotify.com/user/21vzd5cyqwwmnc4usgf24yzjy?si=4d820cde531e47cahttps://open.spotify.com/user/angelakatarina1001?si=b863867521db4297https://open.spotify.com/user/hae3zzfwdxlqb7jhwyxghvqd1?si=5cfb5ecd7f1f4fd6
https://open.spotify.com/user/314vs32d6vzvjnxxto7ye4x6tneu?si=a00bfc76189641f6https://open.spotify.com/user/2oxec3r349m2x7mdwl9u0k7xi?si=db9c881a26134f9ehttps://open.spotify.com/user/317t2q2dztovfc2yzufh5ktt5jee?si=01141a8b8d6c4afehttps://open.spotify.com/user/31ryqvo6cyfciehwvqkjtwa3nt44?si=7bf3fae4183041e9https://open.spotify.com/user/31pvgypjnvjxyooliqcyarhfeahu?si=de66679858d84a8bhttps://open.spotify.com/user/3154bolg6t7edowci4kbhgwx447u?si=0993494a1d0f4a03
"""

user_pattern = re.compile(r"https://open\.spotify\.com/user/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
