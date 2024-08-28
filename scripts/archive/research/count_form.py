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

Input: Sabrina Carpenter - Espresso
1. Doja Cat - Rules 
2. Dominic Fike - Chicken Tenders 
3. Diskoria - Balada Insan Muda  (v)
4. RÜFÜS DU SOL - You Were Right 
5. 5 Seconds of Summer - BLENDER 

Input: Mahalini - Mati-Matian
1. Glenn Fredly - Kisah Yang Salah  (v)
2. Peterpan - Semua Tentang Kita (v) 
3. Fourtwnty - Nyanyian Surau 
4. Mahalini - Sisa Rasa  (v)
5. Kahitna - Takkan Terganti 

Input: Sabrina Carpenter - Please Please Please
1. TLC - Unpretty 
2. Super 7 - BFF - Sahabat 
3. MALIQ & D'Essentials - Yang Pertama  (v)
4. Tokyo Tea Room - Half the Man 
5. もさを。 - 恋色 

CBF_CF

Input: Sabrina Carpenter - Espresso
1. Taylor Swift - Cruel Summer  (v)
2. One Direction - Right Now 
3. The 1975 - It's Not Living (If It's Not With You) 
4. Sheila On 7 - Seberapa Pantas  (v)
5. Conan Gray - Wish You Were Sober 

Input: Mahalini - Mati-Matian
1. Dewa - Risalah Hati 
2. Ari Lasso - Hampa 
3. Pamungkas - One Only  (v)
4. Aziz Hedra - Somebody's Pleasure  (v)
5. RAN - Dekat Di Hati  (v)

Input: Sabrina Carpenter - Please Please Please
1. Taylor Swift - Cruel Summer  (v)
2. Ed Sheeran - Perfect 
3. Pamungkas - To the Bone  (v)
4. Conan Gray - Memories 
5. Sheila On 7 - Seberapa Pantas  (v)

CF

Input: Sabrina Carpenter - Espresso
1. Billie Eilish - BIRDS OF A FEATHER 
2. SZA - Saturn 
3. Sabrina Carpenter - Feather 
4. Tate McRae - greedy 
5. Hozier - Too Sweet 

Input: Mahalini - Mati-Matian
1. Mahalini - Bawa Dia Kembali  (v)
2. Tiara Andini - Janji Setia 
3. Yovie & Nuno - Tanpa Cinta 
4. Juicy Luicy - Tampar  (v)
5. Lyodra - Tak Dianggap  (v)

Input: Sabrina Carpenter - Please Please Please
1. Billie Eilish - BIRDS OF A FEATHER 
2. SZA - Saturn 
3. Tate McRae - greedy  (v)
4. Sabrina Carpenter - Feather  (v)
5. Charli xcx - 360 

CF_CBF

Input: Sabrina Carpenter - Espresso
1. Sabrina Carpenter - Feather (v)
2. Taylor Swift - Cruel Summer (v) 
3. Ariana Grande - the boy is mine (v) 
4. Harry Styles - As It Was  (v)
5. The Chainsmokers - Closer  (v)

Input: Mahalini - Mati-Matian
1. Mahalini - Bawa Dia Kembali  (v)
2. Tiara Andini - Janji Setia  (v)
3. Lyodra - Tak Dianggap  (v)
4. Juicy Luicy - Lantas  (v)
5. Vionita - Dia Masa Lalumu, Aku Masa Depanmu  (v)

Input: Sabrina Carpenter - Please Please Please
1. Sabrina Carpenter - Feather  (v)
2. Ariana Grande - the boy is mine  (v)
3. Taylor Swift - Cruel Summer  (v)
4. Olivia Rodrigo - get him back! 
5. Harry Styles - As It Was (v)
"""

if __name__ == "__main__":
    main(data)
