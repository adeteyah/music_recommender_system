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

Travis Scott - FE!N (feat. Playboi Carti)
1. A$AP Rocky - Houston Old Head 
2. Iwan Fals & NOAH - Yang Terlupakan 
3. Juice WRLD - Black & White 
4. Gerard Way - Maya the Psychic 
5. NF - Let You Down (v)

Billie Eilish - bad guy
1. Doja Cat - Love To Dream (v)
2. Dreane - Pathetic 
3. Petitb - Gohou 
4. Jan Metternich - Mistakes & Heartbreaks 
5. Jayesslee - That's What I Like 

Dewa 19 - Separuh Nafas
1. Dewa 19 - Separuh Nafas (v)
2. T.R.I.A.D - Kuingin Terus Lama Pacaran Disini (Neng Neng Nong Neng) 
3. T.R.I.A.D - Ku Ingin Terus Lama Pacaran Disini - Neng Neng Nong Neng 
4. The SIGIT - Horse 
5. Rocket Rockers - Bangkit 

CBF_CF

Travis Scott - FE!N (feat. Playboi Carti)
1. A$AP Rocky - Houston Old Head (v)
2. Iwan Fals & NOAH - Yang Terlupakan 
3. Juice WRLD - Black & White 
4. Gerard Way - Maya the Psychic 
5. NF - Let You Down (v)

Billie Eilish - bad guy
1. Doja Cat - Love To Dream (v)
2. Dreane - Pathetic 
3. Petitb - Gohou 
4. Jan Metternich - Mistakes & Heartbreaks 
5. Jayesslee - That's What I Like 

Dewa 19 - Separuh Nafas
1. Dewa 19 - Separuh Nafas (v)
2. T.R.I.A.D - Kuingin Terus Lama Pacaran Disini (Neng Neng Nong Neng) 
3. The SIGIT - Horse 
4. Rocket Rockers - Bangkit 
5. Rocket Rockers - Pesta 

CF

Travis Scott - FE!N (feat. Playboi Carti)
1. A Boogie Wit da Hoodie - Still Think About You 
2. BlocBoy JB - Look Alive (feat. Drake) 
3. Yeat - My wrist (with Young Thug) 
4. Yeat - Monëy so big (v)
5. Travis Scott - CIRCUS MAXIMUS (feat. The Weeknd & Swae Lee) (v)

Billie Eilish - bad guy
1. Riton - Rinse & Repeat (feat. Kah-Lo) - Radio Edit 
2. Zac Efron - Rewrite The Stars 
3. Kenshi Yonezu - 死神 
4. Steve Lacy - N Side 
5. BlocBoy JB - Look Alive (feat. Drake) (v)

Dewa 19 - Separuh Nafas
1. Ungu - Saat Bahagia 
2. Dewa 19 - Tak Kan Ada Cinta Yang Lain 
3. Hivi! - Satu-Satunya 
4. Armada - Mabuk Cinta 
5. Dewa - Arjuna (v)

CF_CBF

Travis Scott - FE!N (feat. Playboi Carti)
1. Travis Scott - CAN'T SAY (v)
2. Travis Scott - NO BYSTANDERS (v)
3. ¥$ - CARNIVAL (v)
4. Kanye West - Bound 2 (v)
5. Megan Thee Stallion - BOA 

Billie Eilish - bad guy
1. Billie Eilish - bad guy (with Justin Bieber) 
2. Billie Eilish - Lo Vas A Olvidar (with ROSALÍA) 
3. Lana Del Rey - Money Power Glory (v)
4. Lil Nas X - Old Town Road - Remix 
5. Cardi B - I Like It (v)

Dewa 19 - Separuh Nafas
1. Dewa 19 - Format Masa Depan 
2. Dewa - Separuh Nafas (v)
3. Dewa - Cinta Adalah Misteri (v)
4. T.R.I.A.D - Separuh Nafas (v)
5. Taylor Swift - Fearless (Taylor’s Version)
"""

if __name__ == "__main__":
    main(data)
