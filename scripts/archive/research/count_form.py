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
Mode1 - CBF

My Chemical Romance - The Ghost of You
1. Barenaked Ladies - Too Little Too Late (v)
2. ⁠Rush - Red Barchetta (v)
3. ⁠The Proclaimers - Then It Comes to Me (v)

Kings of Leon - Use Somebody
1. Ty Segall - The Connection Man (v)
2. ⁠The Cure - Dredd Song (v)

Thirty Seconds to Mars - The Kill
1. Breaking Benjamin - Breath (v)
2. ⁠The Used - About You (v)
3. ⁠Good Charlotte - Prayers (v)
4. ⁠Staind - This Is It (v)
5. ⁠Puddle of Mudd - Slide Away (v)

CBF_CF

My Chemical Romance - The Ghost of You
1. Oasis - Champagne Supernova (v)
2. ⁠Deftones - Change (v)
3. ⁠The Killers - Mr Brightside (v)

Kings of Leon - Use Somebody
1. Deftones - Change (v)

Thirty Seconds to Mars - The Kill
1. My Chemical Romance - I'm Not Okay (v)
2. Sum 41 - With Me (v)
3. Muse - Hysteria (v)
4. Good Charlotte - Prayers (v)
5. Thirty Seconds To Mars - Attack  (v)

CF

My Chemical Romance - The Ghost of You
1. My Chemical Romance - Helena (v)
2. blink-182 - All The Small Things (v)
3. Fall Out Boy - Dance, Dance (v)
4. Paramore - Misery Business (v)
5. All Time Low - Dear Maria, Count Me In (v)

Kings of Leon - Use Somebody
1. Kings of Leon - Waste A Moment (v)
2. The Killers - When You Were Young (v)

Thirty Seconds to Mars - The Kill
1. Fall Out Boy - Sugar, We're Goin Down (v)
2. Foo Fighters - Everlong (v)
3. Evanescence - Bring Me To Life (v)
4. Linkin Park - Numb (v)
5. Thirty Seconds To Mars - Closer To The Edge (v))

CF_CBF

My Chemical Romance - The Ghost of You
1. My Chemical Romance - Helena (v)
2. Fall Out Boy - Thnks fr th Mmrs (v)
3. blink-182 - Adam's Song (v)
4. Paramore - Decode (v)
5. Green Day - 21 Guns (v)

Kings of Leon - Use Somebody
1. Kings of Leon - Sex on Fire (v)
2. You Me At Six - Stay With Me (v)
3. Muse - Resistance (v)

Thirty Seconds to Mars - The Kill
1. Thirty Seconds To Mars - Attack (v)
2. Kings of Leon - On Call (v)
"""

if __name__ == "__main__":
    main(data)
