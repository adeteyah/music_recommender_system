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

SadBoyProlific - Dead and Cold
1. SadBoyProlific - Dead and Cold (v)
2. Josh A - Pain 
3. Happily Sad - Why Am I Still Here 
4. Kuzu Mellow - Interstellar 
5. Zach Farache - Sweeterman 

Radiohead - No Surprises
1. Radiohead - No Surprises (v) 
2. Franz Ferdinand - Eleanor Put Your Boots On 
3. Meat Loaf - I'd Do Anything For Love (But I Won't Do That) - Live From The Beacon Theatre, New York, U.S.A./1995 
4. Ari Lasso - Perbedaan 
5. Local Natives - Mt. Washington 

Cigarettes After Sex - K.
1. Jirapah - Matahari 
2. Slowdive - When the Sun Hits 
3. Cigarettes After Sex - Apocalypse (v)
4. my bloody valentine - only tomorrow 
5. Spiritualized - Step into the Breeze 

CBF_CF

SadBoyProlific - Dead and Cold
1. SadBoyProlific - Dead and Cold (v)
2. Josh A - Pain 
3. Happily Sad - Why Am I Still Here 
4. Kuzu Mellow - Interstellar 
5. Zach Farache - Sweeterman 

Radiohead - No Surprises
1. Radiohead - No Surprises (v)
2. Franz Ferdinand - Eleanor Put Your Boots On 
3. Meat Loaf - I'd Do Anything For Love (But I Won't Do That) - Live From The Beacon Theatre, New York, U.S.A./1995 
4. Ari Lasso - Perbedaan 
5. Local Natives - Mt. Washington 

Cigarettes After Sex - K.
1. Jirapah - Matahari 
2. Slowdive - When the Sun Hits 
3. Cigarettes After Sex - Apocalypse (v)
4. my bloody valentine - only tomorrow 
5. Spiritualized - Step into the Breeze 

CF

SadBoyProlific - Dead and Cold
1. Blai$y - World Without You 
2. Kina - Baby You're Worth It (v)
3. Dibyo - Come Thru 
4. Timmies - Loosing Interest 
5. Mishaal Tamer - Kid Goku 

Radiohead - No Surprises
1. Kane Strang - Two Hearts and No Brain 
2. BUBBLE TEA AND CIGARETTES - 5AM Empanada with You 
3. Yahya - keepyousafe 
4. Radiohead - High And Dry 
5. Radiohead - High and Dry 

Cigarettes After Sex - K.
1. Luthfi Aulia - Langit Favorit 
2. Cigarettes After Sex - Silver Sable 
3. Kodaline - Moving On 
4. Cigarettes After Sex - Tejano Blue 
5. Yahya - keepyousafe 

CF_CBF

SadBoyProlific - Dead and Cold
2. Radiohead - No Surprises 

Radiohead - No Surprises
1. Radiohead - Karma Police 
2. Radiohead - Pyramid Song 
3. Cage The Elephant - Rubber Ball - Unpeeled 
4. John Lennon - Imagine - Remastered 2010 
5. Oasis - Stop Crying Your Heart Out 

Cigarettes After Sex - K.
1. Cigarettes After Sex - Apocalypse (v)
2. Cigarettes After Sex - Sesame Syrup 
3. Arctic Monkeys - Why'd You Only Call Me When You're High? (v)
4. Little Mix - Secret Love Song (feat. Jason Derulo) 
5. Henry Moodie - drunk text
"""

if __name__ == "__main__":
    main(data)
