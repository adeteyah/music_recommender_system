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

Avenged Sevenfold - Save Me
1. Atreyu - Becoming the Bull 
2. Linkin Park - From the Inside (v)
3. Evanescence - Everybody's Fool (v)
4. Evanescence - Bring Me To Life 
5. Mötley Crüe - Shout At The Devil 

Kendrick Lamar - Not Like Us
1. Blu DeTiger - Cotton Candy Lemonade 
2. Joey Bada$$ - FOR MY PEOPLE (v)
3. J. Cole - No Role Modelz(v) 
4. Powfu - The Story of the Paper Boy (v)
5. Ella Mai - My Way 

Travis Scott - MY EYES
1. Savanna Leigh - unfamiliar (v)
2. Fressivoir - Summer Fever 
3. Cati Landry - Riptide 
4. Trippie Redd - Love Scars (v)
5. Kodie Osborne - People Change 

CBF_CF

Avenged Sevenfold - Save Me
1. Atreyu - Becoming the Bull 
2. Linkin Park - From the Inside (v)
3. Evanescence - Everybody's Fool (v)
4. Evanescence - Bring Me To Life 
5. Mötley Crüe - Shout At The Devil 

Kendrick Lamar - Not Like Us
1. Blu DeTiger - Cotton Candy Lemonade 
2. Joey Bada$$ - FOR MY PEOPLE (v)
3. J. Cole - No Role Modelz (v)
4. Powfu - The Story of the Paper Boy (v)
5. Ella Mai - My Way 

Travis Scott - MY EYES
1. Savanna Leigh - unfamiliar (v)
2. Fressivoir - Summer Fever 
3. Cati Landry - Riptide 
4. Trippie Redd - Love Scars (v)
5. Kodie Osborne - People Change 

CF

Kendrick Lamar - Not Like Us
1. Metro Boomin - Trance (with Travis Scott & Young Thug) (v)
2. Juice WRLD - Let Me Know (I Wonder Why Freestyle) (v)
3. Lil Baby - Drip Too Hard (Lil Baby & Gunna) 
4. Future - All to Myself 
5. Future - Young Metro (v)

Travis Scott - MY EYES
1. XXXTENTACION - FUXK (feat. Ski Mask the Slump God) (v)
2. Metro Boomin - Trance (with Travis Scott & Young Thug) (v)
3. Juice WRLD - Let Me Know (I Wonder Why Freestyle) (v)
4. Lil Baby - Drip Too Hard (Lil Baby & Gunna) 
5. Future - All to Myself 

CF_CBF

Kendrick Lamar - Not Like Us
1. J. Cole - No Role Modelz (v)
2. Mustard - Parking Lot (v)
3. Offset - Ric Flair Drip (& Metro Boomin) 
4. Mustard - Parking Lot 
5. SZA - Nobody Gets Me 

Travis Scott - MY EYES
1. Travis Scott - I KNOW ? (v)
2. Travis Scott - way back (v)
3. Metro Boomin - Trance (with Travis Scott & Young Thug) 
4. Lil Baby - Freestyle 
5. Kanye West - Praise God
"""

if __name__ == "__main__":
    main(data)
