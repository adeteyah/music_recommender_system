import re
from collections import defaultdict


def parse_input(data):
    """
    Function to parse the input data string into a structured format.
    It returns a dictionary where keys are model names and (v)alues are lists of recommendations.
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
jang, yang punya korelasi sama musik yang di kirim kemarin kasih (v) ya di belakang
contoh: 1. artis - judul (v)

CBF

Juicy Luicy - Lantas
1. Juicy Luicy - Lantas (v)
2. raissa anggiani - Lagi Lagi (v)
3. Sal Priadi - Bulan Yang Baik 
4. Donn - Deserve 
5. Hindia - Evakuasi (v)

Juicy Luicy - Asing
1. Rizky Febian - Seperti Kisah (v)
2. Sunday (1994) - Tired Boy 
3. Payung Teduh - Di Ujung Malam 
4. Tulus - Gajah (v)
5. Juicy Luicy - HAHAHA (v)

HYBS - Ride
1. HYBS - Ride (v)
2. Bruno Mars - Our First Time (v)
3. Ten2Five - You 
4. Ten2Five - You - 2007 Remaster 
5. BRIGHT - Moveไปไหน (Unmovable) / Boys Don't Cry 

CBF_CF

Juicy Luicy - Lantas
1. Juicy Luicy - Lantas (v)
2. raissa anggiani - Lagi Lagi (v)
3. Sal Priadi - Bulan Yang Baik 
4. Donn - Deserve 
5. Hindia - Evakuasi (v)

Juicy Luicy - Asing
1. Rizky Febian - Seperti Kisah (v)
2. Sunday (1994) - Tired Boy 
3. Payung Teduh - Di Ujung Malam 
4. Tulus - Gajah (v)
5. Juicy Luicy - HAHAHA (v)

HYBS - Ride
1. HYBS - Ride (v)
2. Bruno Mars - Our First Time 
3. Ten2Five - You 
4. Ten2Five - You - 2007 Remaster 
5. BRIGHT - Moveไปไหน (Unmovable) / Boys Don't Cry 

CF

Juicy Luicy - Lantas
1. Yura Yunita - Cinta Dan Rahasia (v)
2. Ghea Indrawari - Jiwa Yang Bersedih (v)
3. Ghea Indrawari - Jiwa Yang Bersedih (v)
4. Yovie Widianto - Mantan Terindah 
5. Yovie Widianto - Mantan Terindah 

Juicy Luicy - Asing
1. Yura Yunita - Cinta Dan Rahasia (v)
2. Ghea Indrawari - Jiwa Yang Bersedih (v)
3. Juicy Luicy - Di Balik Layar (v)
4. Nadin Amizah - Rayuan Perempuan Gila (v)
5. Jaz - Berdua Bersama (v)

HYBS - Ride
1. Jeff Bernat - This Time 
2. H.E.R. - Every Kind Of Way (v)
3. Lauv - I Like Me Better (v)
4. HYBS - Dancing with my phone (v)
5. Sleepy Soul - Hazy 

CF_CBF

Juicy Luicy - Lantas
1. Hindia - Evakuasi (v)
2. Andmesh - Andaikan Kau Datang - From "Miracle in Cell No. 7" 
3. Juicy Luicy - Simak (v)
4. Juicy Luicy - Insya Allah (v)
5. Feby Putri - Halu 

Juicy Luicy - Asing
1. Juicy Luicy - HAHAHA (v)
2. Juicy Luicy - Lagu Nikah (v)
3. Rizky Febian - Seperti Kisah (v)
4. Sal Priadi - Mesra-mesraannya kecil-kecilan dulu 
5. Lord Huron - The Night We Met 

HYBS - Ride
1. MIKEY C - Daylight 
2. Aaliyah - At Your Best (You Are Love) 
3. Rainlord. - Call Me 
4. wave to earth - light 
5. Christina Aguilera - Beautiful
"""

if __name__ == "__main__":
    main(data)
