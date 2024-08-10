import re

text = """
https://open.spotify.com/playlist/6aPemTZ8bx1gS0StGKKSfh https://open.spotify.com/playlist/4iDP51wMIQzPbpa9VRUrU4?si=VJ8Nc8mURKqDMX5UzJEjJg&utm_source=copy-link https://open.spotify.com/playlist/2o9kcl8dDvxfaWtOLJUV8T https://open.spotify.com/playlist/1hsKAP7tcyWccdmQHIxIqM https://open.spotify.com/playlist/5dPnPC98nwQgpZhULp9BUS https://open.spotify.com/playlist/7KZB37IRZcbNEIJkmDYJ4D https://open.spotify.com/playlist/29P60CHB8QNSjXGWE4jiDy https://open.spotify.com/playlist/4pq3UdlMTrvenmlwlMHgkn https://open.spotify.com/playlist/50BaWkucoch2d7htodVvWg https://open.spotify.com/playlist/2bWgQNbLBqzsbJrUKNYCkh https://open.spotify.com/playlist/112T4NeLRFqIhR1LVonV95 https://open.spotify.com/playlist/0YYq6IIdB6m1Ec5JS4FzAg https://open.spotify.com/playlist/73qDfNsm32OJm0rtrvw8ro https://open.spotify.com/playlist/5qXRKUDH4k2Z4mfegqHjTT https://open.spotify.com/playlist/2Ommd0HYiS0Wq5Wknf4wNp https://open.spotify.com/playlist/7ii49QRHRrQwXjs9PG3Mqw https://open.spotify.com/playlist/4KRsDF7rO4vaK8njldLBnd https://open.spotify.com/playlist/4oeap4O7HfjrqytrZdmPwl https://open.spotify.com/playlist/3kxzsCC2VrJLDmmkC0jaQU https://open.spotify.com/playlist/77upN7XYbweAUVcT6xo5lf https://open.spotify.com/playlist/1Pf8cB6QegbAsJft7hQliz https://open.spotify.com/playlist/6XnoyH9CgZaG5zbuKg6FpA https://open.spotify.com/playlist/6XeMKFSPpIzviyLuD3xLE7 https://open.spotify.com/playlist/3jpYkBNkAf2xv9tzORrI7U https://open.spotify.com/playlist/3mgQE41HdgweMihea0NhJe https://open.spotify.com/playlist/08YjRzE6G8B7qdv6hNSm4O https://open.spotify.com/playlist/1GqeSqiGBnxLhtRpi9jbPz https://open.spotify.com/playlist/1svlNVVQVzQQ1sD1vJzaX0?si=oG4e0aa_QSWBH6mCjZl6xw&pi=a-5Lnyhnt9RBOo https://open.spotify.com/playlist/3AbFZ7awkFbSRMdVG4a5Uh https://open.spotify.com/playlist/1TGjEgeMreDuCD7itIBKQW https://open.spotify.com/playlist/0ml6XrpZyQoGwgF40Z4LUw https://open.spotify.com/playlist/2K3IS3uRGqWmfdXaMEvKZ3 https://open.spotify.com/playlist/7cZsaeIuICAFDAPyk4suYs https://open.spotify.com/playlist/5QHK4phckDgVxoDTBZZbck https://open.spotify.com/playlist/1fqLr89HNgpxZtphGfQrE6 https://open.spotify.com/playlist/2fyn0MY1s0hcZjV8PnJ0vH https://open.spotify.com/playlist/1zvj5Ovu28GR32Z3ZWTO8Q?si=EIYz8o8dTkWAb5As2OQa2A https://open.spotify.com/playlist/1Wq07CFac4Mk0JjbbxWTHP https://open.spotify.com/playlist/1xK1dZC91G9qLUOoxeA4Sj https://open.spotify.com/playlist/5zc4njUpVEIymv4C0RXA9R
https://open.spotify.com/playlist/2FnzHLgRojDJSQCmMwOy0O
https://open.spotify.com/playlist/17mIXPwdLS4piVL3OzSirt https://open.spotify.com/playlist/1vQ4FvPya39ff8SOGK9Dg9 https://open.spotify.com/playlist/2oNgpLgMohUn5vpRjSIl0b?locale=fr&fo=1 https://open.spotify.com/playlist/1y2AVgn8XHIyqUEsubUf8q https://open.spotify.com/playlist/2n3mF5TsR9zfKKVyJrE9nx https://open.spotify.com/playlist/42J1Kj66rheFPLlV793fG3 https://open.spotify.com/playlist/4hMw676gBE47LgFJ9besjN https://open.spotify.com/playlist/7jIfLeouYwXSD1RlVE6Lvn https://open.spotify.com/playlist/008nxlpV3qXI5lxcfhWsDh https://open.spotify.com/playlist/2pNAHMsOp4OUVej0foJqeY https://open.spotify.com/playlist/5i8Fva3ezh8kKdMusGaIAy https://open.spotify.com/playlist/7imN9ra0n6ZYaVRIqJNu2I https://open.spotify.com/playlist/1dykzQCgKyFpnmbZBZFVV0 https://open.spotify.com/playlist/4pq3UdlMTrvenmlwlMHgkn https://open.spotify.com/playlist/37i9dQZF1E8PVdOo3OE5nV https://open.spotify.com/playlist/2bWgQNbLBqzsbJrUKNYCkh https://open.spotify.com/playlist/5qXRKUDH4k2Z4mfegqHjTT https://open.spotify.com/playlist/2Ommd0HYiS0Wq5Wknf4wNp https://open.spotify.com/playlist/4KRsDF7rO4vaK8njldLBnd https://open.spotify.com/playlist/4oeap4O7HfjrqytrZdmPwl












"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
