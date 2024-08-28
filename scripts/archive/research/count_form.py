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

Input: Linkin Park - Leave Out All The Rest
1. Linkin Park - Leave Out All The Rest (v)
2. James - Getting Away With It (All Messed Up) 
3. Barasuara - Bahas Bahasa 
4. SafetySuit - These Times (v)
5. DIIV - Taker 

Input: ヨルシカ - 春ひさぎ
1. ONE OK ROCK - Outta Sight (v)
2. Hikaru Utada - Simple And Clean 
3. TOKYO CITYPOP CANDY - Just You and I 
4. LiSA - シルシ (v)
5. ZONE - secret base ～君がくれたもの～ (v)

Input: Linkin Park - Leave Out All The Rest
1. Linkin Park - Leave Out All The Rest (v)
2. James - Getting Away With It (All Messed Up) 
3. Barasuara - Bahas Bahasa 
4. SafetySuit - These Times (v)
5. DIIV - Taker 

CBF_CF

Input: Linkin Park - Leave Out All The Rest
1. The 1975 - Robbers 
2. Dewa - Risalah Hati (v)
3. Ari Lasso - Hampa (v)
4. The Neighbourhood - You Get Me So High 
5. Paramore - The Only Exception 

Input: ヨルシカ - 春ひさぎ
1. YOASOBI - あの夢をなぞって (v)
2. ヨルシカ - 言って。 (v)
3. Aimer - 残響散歌 (v)
4. King Gnu - SPECIALZ 
5. Yuuri - ベテルギウス (v)

Input: Linkin Park - Leave Out All The Rest
1. The 1975 - Robbers 
2. Dewa - Risalah Hati (v)
3. Ari Lasso - Hampa (v)
4. The Neighbourhood - You Get Me So High 
5. Paramore - The Only Exception 

CF

Input: Linkin Park - Leave Out All The Rest
1. Linkin Park - Shadow of the Day (v)
2. The Red Jumpsuit Apparatus - Your Guardian Angel 
3. Kings of Leon - Use Somebody 
4. Green Day - Wake Me up When September Ends (v)
5. My Chemical Romance - Cancer (v)

Input: ヨルシカ - 春ひさぎ
3. Linkin Park - Leave Out All The Rest 

Input: Linkin Park - Leave Out All The Rest
1. Linkin Park - Shadow of the Day (v)
2. The Red Jumpsuit Apparatus - Your Guardian Angel 
3. Kings of Leon - Use Somebody 
4. Green Day - Wake Me up When September Ends (v)
5. My Chemical Romance - Cancer (v)

CF_CBF

Input: Linkin Park - Leave Out All The Rest
1. Linkin Park - Shadow of the Day (v)
2. 3 Doors Down - Be Like That 
3. Alter Bridge - In Loving Memory 
4. Creed - One Last Breath (v)
5. Slipknot - Snuff 

Input: ヨルシカ - 春ひさぎ
1. ヨルシカ - 藍二乗 (v)
3. Linkin Park - Leave Out All The Rest 

Input: Linkin Park - Leave Out All The Rest
1. Linkin Park - Shadow of the Day (v)
2. 3 Doors Down - Be Like That 
3. Alter Bridge - In Loving Memory 
4. Creed - One Last Breath (v)
5. Slipknot - Snuff
"""

if __name__ == "__main__":
    main(data)
