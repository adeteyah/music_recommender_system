import re

text = """
https://open.spotify.com/playlist/44dECStrR5ZsA65CVyLQYU https://open.spotify.com/playlist/21irgw7SjQV92eoxgsQ8qz https://open.spotify.com/playlist/4ma35BjBkGqHkRjEpRlISJ https://open.spotify.com/playlist/2S7206SqzFF9ygdbtpaDTc https://open.spotify.com/playlist/1jbh2ixC4hr2zY6FCQHqdY https://open.spotify.com/playlist/37i9dQZF1E4okkxIQpK6il https://open.spotify.com/playlist/1yJna6rc5BTScctXlHrheL https://open.spotify.com/playlist/7B0zxRCJPmTt4qpcZyMZKE https://open.spotify.com/playlist/3nCRb7jOq16ehamjh2Kp8B https://open.spotify.com/playlist/5ibWljqcGdKuDfXaWsj6Nt https://open.spotify.com/playlist/0owD0Svk5iAwCtzgNXL90E https://open.spotify.com/playlist/1uoZ8TOLphLxDcemyLz1Qi https://open.spotify.com/playlist/0NluclHEqEdJUDCm6KpRq7 https://open.spotify.com/playlist/2n5JJJkFQMlmdYOsopsd8n https://open.spotify.com/playlist/1Wjb3MuYOTIv0yZ4rpJ0UI https://open.spotify.com/playlist/1ZpfW6PgyY4xj2g2QsHuJH

https://open.spotify.com/playlist/4aw75vWXpuQLmkp6UwJbfK  https://open.spotify.com/playlist/1jIicCe0Xb18CPLohFYfWS https://open.spotify.com/playlist/5njKxgwZhbIgbObFGUxWm1?autoplay=true https://open.spotify.com/playlist/5zYJZ7s411naUip9oGeIkY https://open.spotify.com/playlist/4jOkCo1gvVMo0GFh0RntCg https://open.spotify.com/playlist/6uBlCLjfx00wsWrhlQTlwm https://open.spotify.com/playlist/1fGCSgZOa8npTz5yGazZJk https://open.spotify.com/playlist/2GLCtZR0CCKgdcNdCK7yfp?go=1&sp_cid=bfb7f31ecd6a5c993278f9e5f85e43af&utm_source=embed_player_p&utm_medium=desktop https://open.spotify.com/playlist/28jRnKzyd2u4YVA4bc9Ml3 https://open.spotify.com/playlist/37i9dQZF1DWW2hj3ZtMbuO https://open.spotify.com/playlist/1AEFyMnt72cwXWTGEUsa2h https://open.spotify.com/playlist/7vcotTAMqdbItFly5KhtpI https://open.spotify.com/playlist/2UIOrIZ403mPKJeTmDt1wq


https://open.spotify.com/playlist/37i9dQZF1E4Ee6Pk9wj4Kf https://open.spotify.com/playlist/6MNyYZLak4uL11bC2t68BA https://open.spotify.com/playlist/4vG6laZTEvcLersv1J5KwV https://open.spotify.com/playlist/7E9BTghuITiafH9t2WsKzd https://open.spotify.com/playlist/1V6hZ3QRhAopFQiqwNIRas








"""
user_pattern = re.compile(
    r"playlist/([a-zA-Z0-9]+)")
matches = user_pattern.findall(text)
unique_usernames = list(set(matches))

print(unique_usernames)
