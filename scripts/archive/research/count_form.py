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

Lyodra - Tak Selalu Memiliki - Ipar Adalah Maut Original Soundtrack
1. Orion 001 - Tentram - Original Motion Picture Soundtrack 
2. Virgoun - Bukti (v)
3. Ratu - Dear Diary (v)
4. Ecoutez - Percayalah (v)
5. Rio Febrian - Aku Bertahan (v)

Sabrina Carpenter - Espresso
1. With Confidence - Pâquerette (Without Me) (v)
2. Stand Atlantic - Skinny Dipping (v)
3. Jacob Sartorius - All My Friends (v)
4. Apink - Be Myself 
5. BOL4 - Some 

Red Velvet - Cosmic
1. Red Velvet - Color of Love (v)
2. MONSTA X - If with U 
3. NCT DOJAEJUNG - Perfume 
4. IU - Blueming (v)
5. WINNER - LOVE ME LOVE ME 

CBF_CF

Lyodra - Tak Selalu Memiliki - Ipar Adalah Maut Original Soundtrack
1. Orion 001 - Tentram - Original Motion Picture Soundtrack 
2. Virgoun - Bukti  (v)
3. Ratu - Dear Diary  (v)
4. Ecoutez - Percayalah  (v)
5. Rio Febrian - Aku Bertahan  (v)

Sabrina Carpenter - Espresso
1. With Confidence - Pâquerette (Without Me)  (v)
2. Stand Atlantic - Skinny Dipping  (v)
3. Jacob Sartorius - All My Friends  (v)
4. Apink - Be Myself 
5. BOL4 - Some 

Red Velvet - Cosmic
1. Red Velvet - Color of Love  (v)
2. MONSTA X - If with U 
3. NCT DOJAEJUNG - Perfume 
4. IU - Blueming  (v)
5. WINNER - LOVE ME LOVE ME 

CF

Lyodra - Tak Selalu Memiliki - Ipar Adalah Maut Original Soundtrack
1. Geisha - Karena Kamu  (v)
2. SAMSONS - Kenangan Terindah  (v)
3. Vionita - Dia Masa Lalumu, Aku Masa Depanmu (v)
4. Judika - Putus Atau Terus  (v)
5. Mahalini - Bohongi Hati  (v)

Sabrina Carpenter - Espresso
1. d4vd - Feel It - From The Original Series “Invincible” (v)
2. Regard - You (v)
3. Ruel - Painkiller (v)
4. Raphael DeLove - The Man Who Can't Be Moved (v)
5. lovelytheband - broken 

Red Velvet - Cosmic
1. RIIZE - Get A Guitar 
2. Lim Young Woong - Love Always Run Away 
3. Kim MinSeok - DrunKen Confession 
4. TAEYEON - Dream (v)
5. RIIZE - Love 119 

CF_CBF

Lyodra - Tak Selalu Memiliki - Ipar Adalah Maut Original Soundtrack
1. Virgoun - Orang Yang Sama (v)
2. Yovie & Nuno - Mengejar Mimpi (v)
3. Afgan - Bukan Cinta Biasa (v)
4. Afgan - Kamu Yang Kutunggu (v)
2. Sabrina Carpenter - Espresso 

Sabrina Carpenter - Espresso
1. Taylor Swift - 22 (v)
2. The Chainsmokers - Something Just Like This (v)
3. Taylor Swift - Picture To Burn (v)
4. Sabrina Carpenter - bet u wanna (v)
5. Ariana Grande - Moonlight (v)

Red Velvet - Cosmic
1. NewJeans - Attention (v)
2. NewJeans - Bubble Gum (v)
3. RIIZE - Siren 
4. BTS - 봄날 (v)
"""

if __name__ == "__main__":
    main(data)
