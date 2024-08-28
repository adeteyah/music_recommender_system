import re
from collections import defaultdict


def parse_input(data):
    """
    Function to parse the input data string into a structured format.
    It returns a dictionary where keys are model names and values are lists of recommendations.
    """
    model_data = defaultdict(list)
    current_model = None

    for line in data.splitlines():
        line = line.strip()

        # Check if the line is a model name
        if re.match(r'^[A-Z_]+$', line):
            current_model = line
            model_data[current_model] = []
        elif current_model and line:
            # Append the line to the current model's recommendations
            model_data[current_model].append(line)

    return model_data


def calculate_true_positives_and_total(recommendations):
    """
    Function to calculate True Positives and Total Recommendations from a list of recommendations.
    Returns a tuple: (list of True Positives, total number of recommendations, array of TP and FP).
    """
    true_positives = []
    total_recommendations = []
    tp_fp_array = []

    i = 0
    while i < len(recommendations):
        # Find the start of a new song (indicated by no preceding number)
        if not re.match(r'^\d+\.\s', recommendations[i]):
            tp_count = 0
            song_total = 0
            song_array = []
            # Check subsequent lines for '(v)' markers until the next song title or end of list
            i += 1
            while i < len(recommendations) and re.match(r'^\d+\.\s', recommendations[i]):
                song_total += 1
                if '(v)' in recommendations[i]:
                    tp_count += 1
                    song_array.append(1)
                else:
                    song_array.append(0)
                i += 1
            true_positives.append(tp_count)
            total_recommendations.append(song_total)
            tp_fp_array.extend(song_array)
        else:
            i += 1

    return true_positives, total_recommendations, tp_fp_array


def main(data):
    model_data = parse_input(data)

    # Define the desired order of models
    model_order = ["CF", "CBF", "CF_CBF", "CBF_CF"]

    results = {}

    for model_name in model_order:
        if model_name in model_data:
            tps, totals, tp_fp_array = calculate_true_positives_and_total(
                model_data[model_name])
            results[model_name] = (tps, totals, tp_fp_array)

    # Output results in a simplified format
    for model_name in model_order:
        if model_name in results:
            tps, totals, tp_fp_array = results[model_name]
            print(f"{model_name}:")
            print(f"  - Total True Positives (all items): {sum(tps)}")
            print(f"  - Total Recommendations (all items): {sum(totals)}")
            print(f"  - True Positives per Item: {tps}")
            print(f"  - Recommendations per Item: {totals}")
            print(f"  - TP/FP Array: {tp_fp_array}\n")


# Example input
data = """
CBF

SONGS RECOMMENDATION: https://open.spotify.com/track/30Z12rJpW0M0u8HMFpigTB Troye Sivan - Angel Baby
1. https://open.spotify.com/track/2m6Ko3CY1qXNNja8AlugNc Troye Sivan - Angel Baby (v)
2. https://open.spotify.com/track/0k0SZljUKvFGGnWS3fHaU4 Everything Everything - Big Game (v)
3. https://open.spotify.com/track/7p8GWclbwHuUxwom7c1oRz SiR - Love You 
4. https://open.spotify.com/track/6l3vk93IWfe0wq396JTCM6 One Direction - Over Again (v)
5. https://open.spotify.com/track/7Emma5nwTSZicLLAC7uS1m La Bouche - Say You'll Be Mine 

SONGS RECOMMENDATION: https://open.spotify.com/track/1PfpeMO6uUNGfs3VJOrdGH Henry Moodie - drunk text
1. https://open.spotify.com/track/6EIMUjQ7Q8Zr2VtIUik4He Henry Moodie - drunk text (v)
2. https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v Ed Sheeran - Perfect (v)
3. https://open.spotify.com/track/4BIuY0oEopXizyP3WvkNrT Valley - Oh shit…are we in love? 
4. https://open.spotify.com/track/4yNk9iz9WVJikRFle3XEvn JVKE - golden hour (v)
5. https://open.spotify.com/track/7MOCaEUbfGyq1K96umNVwJ Jessie Murph - Pray 

SONGS RECOMMENDATION: https://open.spotify.com/track/5Ho92lX5GVGgcJSkUA9sPi Wafia - Hurts (feat. Louis The Child & Whethan)
1. https://open.spotify.com/track/05sp2EySV6DXsKLeBnjaK0 Backstreet Boys - Anywhere for You (v)
2. https://open.spotify.com/track/4Ay9gCblPwpQBYkw0jpnNE Jennifer Love Hewitt - You (v)
3. https://open.spotify.com/track/5u2TIRt6MDr1m6xQ9JNYp0 Lily Allen - Sheezus (v)
4. https://open.spotify.com/track/4jJvCViucp63pJTOgJF0iG Melanie C - Good Enough 
5. https://open.spotify.com/track/2rbDhOo9Fh61Bbu23T2qCk Lady Gaga - Always Remember Us This Way (v)

CBF_CF

SONGS RECOMMENDATION: https://open.spotify.com/track/30Z12rJpW0M0u8HMFpigTB Troye Sivan - Angel Baby
1. https://open.spotify.com/track/0cc9lgdfHqeS8t9BzbFFmj Dewa - Risalah Hati (v)
2. https://open.spotify.com/track/0GgN4MhR5GKn5IcKN0e0rG My Chemical Romance - Cancer 
3. https://open.spotify.com/track/6bE0o9hYUPYlokZIH79oM0 Ari Lasso - Hampa (v)
4. https://open.spotify.com/track/5h51lTy1jYDDkYLALQrzX9 Pamungkas - Risalah Hati 
5. https://open.spotify.com/track/0InJPuWIYp8fwlBGIQglLf Maudy Ayunda - Perahu Kertas (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/68QJLyclURexWWrjTAQMN2 Henry Moodie - drunk text
1. https://open.spotify.com/track/0tgVpDi06FyKpA1z0VMD4v Ed Sheeran - Perfect (v)
2. https://open.spotify.com/track/2QdVcmVPIxW826rRJDf58l Ruel - Face To Face 
3. https://open.spotify.com/track/4yNk9iz9WVJikRFle3XEvn JVKE - golden hour (v)
4. https://open.spotify.com/track/7MOCaEUbfGyq1K96umNVwJ Jessie Murph - Pray (v)
5. https://open.spotify.com/track/6EIMUjQ7Q8Zr2VtIUik4He Henry Moodie - drunk text (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/00cBcYOlnHoXX9ver3cmdE Wafia - Hurts (feat. Louis The Child & Whethan)
1. https://open.spotify.com/track/3Vi5XqYrmQgOYBajMWSvCi Doja Cat - Need to Know (v)
2. https://open.spotify.com/track/2rbDhOo9Fh61Bbu23T2qCk Lady Gaga - Always Remember Us This Way (v)
3. https://open.spotify.com/track/73ucpKq91TuejrLHgzDNHK Rita Ora - Poison (v)
4. https://open.spotify.com/track/7o9uu2GDtVDr9nsR7ZRN73 Cyndi Lauper - Time After Time (v)
5. https://open.spotify.com/track/1lkvpmrCaXK8QtliFDcHBO Colbie Caillat - Bubbly (v)

CF

SONGS RECOMMENDATION: https://open.spotify.com/track/3wlLknnMtD8yZ0pCtCeeK4 Troye Sivan - Angel Baby
1. https://open.spotify.com/track/3afkJSKX0EAMsJXTZnDXXJ Troye Sivan - Strawberries & Cigarettes (v)
2. https://open.spotify.com/track/4HBZA5flZLE435QTztThqH Ariana Grande - Stuck with U (with Justin Bieber) (v)
3. https://open.spotify.com/track/5O2P9iiztwhomNh8xkR9lJ One Direction - Night Changes (v)
4. https://open.spotify.com/track/0ClPIeT6MSgfSgQ9ZrJbAq Charlie Puth - Cheating on You (v)
5. https://open.spotify.com/track/2eAvDnpXP5W0cVtiI0PUxV Ruth B. - Dandelions (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/0KpWiHVmIFDTvai20likX4 Henry Moodie - drunk text
1. https://open.spotify.com/track/2tGvwE8GcFKwNdAXMnlbfl Olivia Rodrigo - happier (v)
2. https://open.spotify.com/track/5ajjAnNRh8bxFvaVHzpPjh Madison Beer - Reckless (v)
3. https://open.spotify.com/track/5O2P9iiztwhomNh8xkR9lJ One Direction - Night Changes (v)
4. https://open.spotify.com/track/1daDRI9ahBonbWD8YcxOIB Miley Cyrus - Angels Like You (v)
5. https://open.spotify.com/track/1ei3hzQmrgealgRKFxIcWn Benson Boone - In The Stars (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/30Z12rJpW0M0u8HMFpigTB Wafia - Hurts (feat. Louis The Child & Whethan)
1. https://open.spotify.com/track/4kL66iksPrNaqzKYlzDgoa Louis The Child - Breaking News (with RAYE) (v)
2. https://open.spotify.com/track/5YPfFN0EsuvOgisgC4tzBq Whethan - Summer Luv (feat. Crystal Fighters) (v)
3. https://open.spotify.com/track/3yydZof4pq6N4zeyTzLwQk RAC - Passion 
4. https://open.spotify.com/track/0qQCWMHz32bQd8gIKc8LFd Elderbrook - Dominoes 
5. https://open.spotify.com/track/4JiuLIWKkLH2iluzOhXh5Y SG Lewis - Flames (feat. Ruel) (v)

CF_CBF

SONGS RECOMMENDATION: https://open.spotify.com/track/3wlLknnMtD8yZ0pCtCeeK4 Troye Sivan - Angel Baby
1. https://open.spotify.com/track/3afkJSKX0EAMsJXTZnDXXJ Troye Sivan - Strawberries & Cigarettes (v)
2. https://open.spotify.com/track/2uEJanMvnA1dXgX1ASnPQm Charlie Puth - One Call Away (v)
2. https://open.spotify.com/track/0KpWiHVmIFDTvai20likX4 Henry Moodie - drunk text (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/0KpWiHVmIFDTvai20likX4 Henry Moodie - drunk text
1. https://open.spotify.com/track/1ei3hzQmrgealgRKFxIcWn Benson Boone - In The Stars (v)
2. https://open.spotify.com/track/5iKyrrKFZ9zHbW0mpW18GA Henry Moodie - closure (v)
3. https://open.spotify.com/track/30Z12rJpW0M0u8HMFpigTB Wafia - Hurts (feat. Louis The Child & Whethan) (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/30Z12rJpW0M0u8HMFpigTB Wafia - Hurts (feat. Louis The Child & Whethan)
1. https://open.spotify.com/track/7Ga9ZSdPAcQXQvd1ObVFpm Galantis - Holy Water (v)
2. https://open.spotify.com/track/0kEzNFvi5ZOlwn6ly5DR8i Doja Cat - Boss Bitch 
3. https://open.spotify.com/track/7JHdotEeGSIbtFuo4dVvsC Alesso - In The Middle (v)
4. https://open.spotify.com/track/5ZZrcH8ZMuCWCxGoWoyjey Robyn - Missing U (v)
5. https://open.spotify.com/track/7qXRE8SYTVU74cUdBgFSvt Jax Jones - This is Real (v)
"""

if __name__ == "__main__":
    main(data)
