import re

text = """

https://open.spotify.com/playlist/5xQq0MwAAmDj8Uf0VoqjB1?si=b20ac7772c004b49 https://open.spotify.com/playlist/1pL4wy7kkh5HM0l2YesCDS?si=93f90c0364bd4886 https://open.spotify.com/playlist/3FlH406IC8CiVAi1MKmqVa?si=4e26cbcf4ae04118 https://open.spotify.com/playlist/72btHatYgasyS7hhy3VrXK?si=d1092a4467de4dcf https://open.spotify.com/playlist/3wli5NEUYQyBtH7zkIkqPB?si=0a60c5e92b974dff https://open.spotify.com/playlist/2XNzKHS14q8zik7YtBdUEi?si=06dc5e99b6044780 https://open.spotify.com/playlist/6AiEY0DPXzmA27mLk6cQ13?si=2486b21c384144e3 https://open.spotify.com/playlist/5shCdZFhwo2PqRYfE62AWI?si=187c2858ebe54adc https://open.spotify.com/playlist/2V8mpK05BVsMPEWx1cEpG9?si=63e5812139314e08 https://open.spotify.com/playlist/5RI20Ct0QlIV6REv9neVCS?si=8f199c6028074eb3 https://open.spotify.com/playlist/2y5W549SOvoXkmKV5ruDDb?si=71723702c1ca4eb6 https://open.spotify.com/playlist/2CjnaMVrNh3NJaFmDNKHMj?si=889ae0ea112d467a https://open.spotify.com/playlist/1GoBCL2tGsDYb8w4m9XTEt?si=f0ed46c66bba4743 https://open.spotify.com/playlist/7CRDwHmFIWIFakS8whUz5e?si=98f038548f264061 https://open.spotify.com/playlist/7z3sSuBECJNcWAHwrLcLyQ https://open.spotify.com/playlist/1COUHhhrqMcoe90qn2EWiH https://open.spotify.com/playlist/0Qy8n31ndQcDYMBXBP4g5P https://open.spotify.com/playlist/25PIacuEBRtcyhygXzV0U6 https://open.spotify.com/playlist/1JVP02FYKSm08iciezMybx https://open.spotify.com/playlist/7p4qH3gGsrTHpwmsby0awh https://open.spotify.com/playlist/6bw7e3xgXp5vvKG8UC6KYM https://open.spotify.com/playlist/2db0y17l9Dw0FMEvIH5c83 https://open.spotify.com/playlist/0ptCCEWuYh1wgKaHSAtkeB?autoplay=true https://open.spotify.com/playlist/5Lo7a936yE5kqutpNt4i7c https://open.spotify.com/playlist/3yuhAxr6DzD8G9RxdWZq9F https://open.spotify.com/playlist/3oOyEJnrgNOv4AxiMWimNt https://open.spotify.com/playlist/5tg0VHViwlCRayFmZEb89a https://open.spotify.com/playlist/3hrrAThqaEkcTi7swVwbOK https://open.spotify.com/playlist/0lQKHzupvlwYzfxUFuwnvc https://open.spotify.com/playlist/2Bpa4HFfIx40AHulclotZH https://open.spotify.com/playlist/0FKSk9sjaHsNVUVYswpx9p https://open.spotify.com/playlist/0HYqwURYvhkcmy7AqnXpTh https://open.spotify.com/playlist/3BrGODBakPhEIHyR5kSCsV
https://open.spotify.com/playlist/6jkBTwKqoI9RIavyXfKvDa https://open.spotify.com/playlist/0LADki212SVjINOgJP0VUw https://open.spotify.com/playlist/3TbA86BfTc0HiwzwSOLznG https://open.spotify.com/playlist/3gY62YegpVZDU2OCNvpXqI https://open.spotify.com/playlist/0zNakzrvsAdoiXELta1Cfv https://open.spotify.com/playlist/78QB58T7RSHnHAQQjLtoWA https://open.spotify.com/playlist/3PBsUVcXZz8wK70UwruDG9 https://open.spotify.com/playlist/2TI7DRbHGKN19uRnXFKWfF https://open.spotify.com/playlist/41cU4G49XQlcpTJa6I5wfu https://open.spotify.com/playlist/4KIOolK4mCsjG1grjd7jXN https://open.spotify.com/playlist/37i9dQZF1E4Br0HS2FHp4J https://open.spotify.com/playlist/37i9dQZF1E4xFviXynxYbB https://open.spotify.com/playlist/5pKglxKhR3DiFrPNHSKpGN https://open.spotify.com/playlist/29ZnOCY80NlBGMuTGdVbHc https://open.spotify.com/playlist/37JUrZGesBv1BoJQpbWsnv







"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
