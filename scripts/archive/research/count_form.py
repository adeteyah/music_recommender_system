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

mitei - excuses for losing touch
1. Naomi Scott - Speechless (Full) 
2. American Authors - Deep Water - Acoustic 
3. Cavetown - Home 
4. Shawn Mendes - Use Somebody - Recorded at Spotify Studios NYC 
5. Our Story - Kisah Kelam 

Bring Me The Horizon - DiE4u
1. Hollywood Undead - Coming Home 
2. Bloc Party - This Modern Love 
3. A Day To Remember - All I Want 
4. Bring Me The Horizon - Avalanche (v)
5. Florence + The Machine - Heavy In Your Arms 

Porter Robinson - Get Your Wish
1. Madeon - Be Fine (v)
2. Alison Wonderland - Church 
3. WHENSDAY - Alright 
4. Madeon - No Fear No More
5. Switch - Angels We Have Heard On High 

CBF_CF

mitei - excuses for losing touch
1. Naomi Scott - Speechless (Full) 
2. American Authors - Deep Water - Acoustic 
3. Cavetown - Home 
4. Shawn Mendes - Use Somebody - Recorded at Spotify Studios NYC 
5. Our Story - Kisah Kelam 

Bring Me The Horizon - DiE4u
1. Hollywood Undead - Coming Home 
2. Bloc Party - This Modern Love 
3. A Day To Remember - All I Want 
4. Bring Me The Horizon - Avalanche (v) 
5. Florence + The Machine - Heavy In Your Arms 

Porter Robinson - Get Your Wish
1. Madeon - Be Fine (v)
2. Alison Wonderland - Church 
3. WHENSDAY - Alright 
4. Madeon - No Fear No More 
5. Switch - Angels We Have Heard On High 

CF

mitei - excuses for losing touch
1. a r u k a. - caustics (v)
2. D'art- - Paper cup telephone (v)
3. a r u k a. - smells like earth (v)
4. Neck Deep - Empty House 
5. Kogane - Around You - lalanoi Remix (v)

Bring Me The Horizon - DiE4u
1. MIKA - Yo Yo 
2. Trevor Daniel - Falling (feat. blackbear) - blackbear Remix 
3. Call Me Karizma - I Fell in Love with My Best Friend 
4. Gotye - Somebody That I Used To Know 
5. Taylor Swift - Wildest Dreams 

Porter Robinson - Get Your Wish
1. Porter Robinson - Lionhearted (v)
2. Lucas & Steve - I Want It All 
3. Bag Raiders - Shooting Stars 
4. Clean Bandit - Rather Be (feat. Jess Glynne) 
5. Mat Zo - Easy - Extended Remix 

CF_CBF

mitei - excuses for losing touch
1. D'art- - Paper cup telephone (v)
2. small house in spain - tether weight ₊˚✧•° .* (v)
3. N33T - jellyfish (v)
4. phritz - look at the sky (v)
2. Bring Me The Horizon - DiE4u 

Bring Me The Horizon - DiE4u
1. Bring Me The Horizon - Avalanche (v)
2. Bring Me The Horizon - Avalanche (v)
3. Hollywood Undead - Coming Home 
4. AFI - Twisted Tongues (v)
5. Daughtry - Heavy Is The Crown (v)

Porter Robinson - Get Your Wish
1. Porter Robinson - Goodbye To A World (v)
2. Porter Robinson - Polygon Dust (v)
3. Madeon - The Prince 
4. Madeon - Be Fine (v)
5. Martin Garrix - There For You - Lione Remix
"""

if __name__ == "__main__":
    main(data)
