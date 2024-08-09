import re

text = """
https://open.spotify.com/playlist/768SflksbwuG1jZBTK7RMl?si=8442257919de4253 https://open.spotify.com/playlist/1nVVC9Svad20T7Cv6QXKDU?si=68bd27b7471b4c0a https://open.spotify.com/playlist/72uikYQTHHCN0uv5xPUmmX?si=cd67e8b7b8a649d9 https://open.spotify.com/playlist/05EEepiMvy9vpUbuLAZHnw?si=a4dcf75016f84ee4 https://open.spotify.com/playlist/7kGrCvbC65n8ghclNM2HUz?si=054f059dfb864c3a https://open.spotify.com/playlist/1ARteKWocOWh9BOW1pLdRE?si=dfb733d045674ca8 https://open.spotify.com/playlist/70XwOfkGae10QrIWab1fDk?si=036888f083ef478c https://open.spotify.com/playlist/4XEKCxYbqLBEZnHNqCWf6Q?si=ed5aff28c2e0473c https://open.spotify.com/playlist/5Y7YdKAksCWnAsdjq51dsj?si=62c0a7aae3a3448f https://open.spotify.com/playlist/02jSFJfBPIvKTGGrlTAWhM?si=ccd471192f5544f5 https://open.spotify.com/playlist/7ii49QRHRrQwXjs9PG3Mqw?si=2cb2417decd14d16 https://open.spotify.com/playlist/6O6YHgNv2mPHJrNFhuJFHA?si=bea29ff718324c0d https://open.spotify.com/playlist/0Yah2D11WPmTuONCPpF3qn?si=cbdf8e877fd74ef4 https://open.spotify.com/playlist/5Jnn0VNHO7VOh9uC9lbsUL?si=c6cab0d7fa184f84 https://open.spotify.com/playlist/6RMdHyE9qWmgIw5NldVOgw?si=241f8f8e90e74663 https://open.spotify.com/playlist/24fxepcPPddsy2EGxIZnAi?si=cb3d15b4bad94333 https://open.spotify.com/playlist/67H0yLaRm7WmkXOdCWcT3C?si=82e4f798c4134a01 https://open.spotify.com/playlist/29C4QuiH7GdGaaskykqPFE?si=a21b827f4d3f4bf2 https://open.spotify.com/playlist/6BF4wTjkkPAiiGGzneBDSN?si=3ee70348ec884680 https://open.spotify.com/playlist/573kYuA2F1cxEBwQmPIykJ?si=ba4af8e4ba1d44d1 https://open.spotify.com/playlist/5qSmvjITVRNAcSRBCa2tJ9?si=a544454809f74625 https://open.spotify.com/playlist/42GFU1nwXyhr49SZZvCyHp?si=62dc835f2511405e https://open.spotify.com/playlist/7MGp4zp5Y2MKv910jLWgeB?si=7b24454c172040ce https://open.spotify.com/playlist/5veskluu57QYm2Q6TZXq34?si=15e6f69a8bb74aed https://open.spotify.com/playlist/1inVPhYK6TDVlKqZbApdcl?si=80a1e290b914452e https://open.spotify.com/playlist/3Uo6wcwipB5JtMBtDk1msK?si=83426197c44c40b7 https://open.spotify.com/playlist/4sBiRN7TNGxpm6keqyF2dH?si=c8d48c991fd44f35 https://open.spotify.com/playlist/40sNn0bHB6bd0AnogyHoXd?si=6db126882cb6424f https://open.spotify.com/playlist/5AXoVexX6nykYyVlkZFobP https://open.spotify.com/playlist/68Kdkdo67uUtbNn6m2Incn https://open.spotify.com/playlist/72MmIAbC21g5Ge2EsY9qVP https://open.spotify.com/playlist/03NJ2WW9cm04tHLZzgck7N https://open.spotify.com/playlist/4Tdv7hOcUK16qHjjQjUiuq https://open.spotify.com/playlist/0XbZRYyRdlRCF5QbP8QkmQ











"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
