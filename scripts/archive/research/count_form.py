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

D.O. - Popcorn
1. D.O. - Popcorn (v)
2. SHINee - Sleepless Night 
3. BOL4 - My Trouble (v)
4. Eric Nam - Before the Sunset 
5. MINNIE - Like A Dream 

Bernadya - Satu Bulan
1. Sal Priadi - Bulan Yang Baik (v)
2. Chrisye - Seperti Yang Kau Minta 
3. Angga Candra - Sedihku (Sekecewa Itu 2) 
4. Tulus - Ingkar (v)
5. raissa anggiani - Lagi Lagi (v) 

SEVENTEEN - Cheers to youth
1. TRI.BE - LORO 
2. AKMU - Be With You 
3. NCT 127 - Elevator (127F) (v)
4. George Ezra - Blame It on Me 
5. Apink - Be Myself 

CBF_CF 

D.O. - Popcorn
1. D.O. - Popcorn (v)
2. SHINee - Sleepless Night 
3. BOL4 - My Trouble (v)
4. Eric Nam - Before the Sunset 
5. MINNIE - Like A Dream 

Bernadya - Satu Bulan
1. Sal Priadi - Bulan Yang Baik 
2. Angga Candra - Sedihku (Sekecewa Itu 2) 
3. Tulus - Ingkar (v)
4. raissa anggiani - Lagi Lagi (v)
5. Andmesh - Andaikan Kau Datang - From "Miracle in Cell No. 7" 

SEVENTEEN - Cheers to youth
1. TRI.BE - LORO 
2. AKMU - Be With You (v)
3. George Ezra - Blame It on Me 
4. Apink - Be Myself 
5. LE SSERAFIM - FEARLESS (2023 Ver.) (v) 

CF 

D.O. - Popcorn
1. BIG Naughty - IMFP 
2. EXO - Sweet Lies (v)
3. Jimmy Brown - Let Me Know 
4. D.O. - That's okay (v)
5. EXO - Miracles in December (v) 

Bernadya - Satu Bulan
1. Boyz II Men - On Bended Knee 
2. raissa anggiani - Losing Us. (v)
3. Mocca - I Remember - 2017 Version (v)
4. Nadin Amizah - Beranjak Dewasa (v)
5. Hanin Dhiya - Biar Waktu Hapus Sedihku 

SEVENTEEN - Cheers to youth
1. BSS - The Reasons of My Smiles (v)
2. ENHYPEN - XO (Only If You Say Yes) 
3. SEVENTEEN - Anyone (v)
4. TOMORROW X TOGETHER - Deep Down 
5. SEVENTEEN - Lie Again (v) 

CF_CBF 

D.O. - Popcorn
1. DAY6 - Welcome to the Show 
2. ECLIPSE - Run Run 
3. Pagaehun - Play With Me 
4. EXO-CBX - Paper Cuts 
5. CHEN - An Unfamiliar Day (v) 

Bernadya - Satu Bulan
1. Juicy Luicy - Lantas 
2. Hal - terima kasih 
3. Juicy Luicy - Simak 
4. raissa anggiani - Lagi Lagi (v)
5. Ariana Grande - intro (end of the world) 

SEVENTEEN - Cheers to youth
1. Gyubin - Really Like You 
2. TOMORROW X TOGETHER - 0X1=LOVESONG (I Know I Love You) feat. Seori 
3. SEVENTEEN - BRING IT (v)
4. DAY6 - days gone by 
5. BTS - Telepathy (v)
"""

if __name__ == "__main__":
    main(data)
