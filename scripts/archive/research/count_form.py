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
dee, yang punya korelasi sama musik yang di kirim kemarin kasih (v) ya di belakang
contoh: 1. artis - judul (v)

CBF

ENHYPEN - SHOUT OUT
1. THEIA - High 
2. HUH YUNJIN - I ≠ DOLL 
3. Wanna One - Beautiful (v)
4. ASTRO - ONE&ONLY 
5. DAY6 - Afraid 

TREASURE - GOING CRAZY
1. TOMORROW X TOGETHER - Sugar Rush Ride (v)
2. Wanna One - Energetic (v)
3. SUPER JUNIOR - 미인아 Bonamana 
4. 2PM - Hands Up (v)
5. Mathilde SPZ - (In Your Mind) I´m Naked 

NIKI - High School in Jakarta
1. NIKI - High School in Jakarta (v)
2. Susan Carol - Green and Brown 
3. Raisa - Teka Teki (v)
4. Isyana Sarasvati - Tetap Dalam Jiwa (v)
5. Arash Buana - lmao i just broke up 

CBF_CF

ENHYPEN - SHOUT OUT
1. THEIA - High 
2. HUH YUNJIN - I ≠ DOLL 
3. Wanna One - Beautiful (v)
4. DAY6 - Afraid 
5. Stray Kids - DOMINO 

TREASURE - GOING CRAZY
1. TOMORROW X TOGETHER - Sugar Rush Ride (v)
2. Wanna One - Energetic (v)
3. SUPER JUNIOR - 미인아 Bonamana 
4. 2PM - Hands Up (v)
5. Mathilde SPZ - (In Your Mind) I´m Naked 

NIKI - High School in Jakarta
1. NIKI - High School in Jakarta (v)
2. Susan Carol - Green and Brown 
3. Raisa - Teka Teki (v)
4. Isyana Sarasvati - Tetap Dalam Jiwa (v)
5. Arash Buana - lmao i just broke up 

CF

ENHYPEN - SHOUT OUT
1. ENHYPEN - Chaconne (v)
2. ENHYPEN - Lucifer 
3. I-LAND - Calling (Run To You) 
4. I-LAND - Calling (Run To You) 
5. Pamungkas - To the Bone (v)

TREASURE - GOING CRAZY
1. NCT 127 - Regular - Korean Version (v)
2. ENHYPEN - Drunk-Dazed (v)
3. NCT DREAM - Drippin' (v)
4. TREASURE - HELLO (v)
5. NCT 127 - Simon Says (v)

NIKI - High School in Jakarta
1. Far East Movement - Freal Luv (feat. Marshmello, Chanyeol & Tinashe) 
2. Westlife - Uptown Girl - Radio Edit 
3. NewJeans - Super Shy (v)
4. NIKI - Nightcrawlers 
5. Mr. Big - Wild World - 2009 Remastered Version 

CF_CBF

ENHYPEN - SHOUT OUT
1. ENHYPEN - Forget Me Not 
2. ENHYPEN - Outro : Cross the Line 
3. Dreamcatcher - Silent Night 
4. Dreamcatcher - Trap 
5. Skinny Brown - No! Go Back (Feat. Han Yo Han) 

TREASURE - GOING CRAZY
1. TOMORROW X TOGETHER - Sugar Rush Ride (v)
2. IVE - After LIKE (v)
3. aespa - YEPPI YEPPI 
4. Red Velvet - Red Flavor (v)
5. XODIAC - SPECIAL LOVE 

NIKI - High School in Jakarta
1. NIKI - Milk Teeth 
2. NIKI - Milk Teeth 
3. Carly Rae Jepsen - Call Me Maybe 
4. Taylor Swift - How You Get The Girl 
5. Rex Orange County - THE SHADE (v)
"""

if __name__ == "__main__":
    main(data)
