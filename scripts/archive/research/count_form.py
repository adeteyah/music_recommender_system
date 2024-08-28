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

Yuuri - ドライフラワー
1. Yuuri - ドライフラワー (v)
2. Ado - ドライフラワー (v)
3. Tani Yuuki - Aikotoba (v)
4. Tani Yuuki - 愛言葉 (v)
5. ONE OK ROCK - We Are (v)

Lee Mujin - Traffic light
1. KyoungSeo - 120BPM (v)
2. CHEEZE - Mood Indigo 
3. Lee Mujin - Propose (v)
4. BIG Naughty - IMFP 
5. DAY6 (Even of Day) - so this is love 

Ed Sheeran - Galway Girl
1. Citra Scholastika - Pasti Bisa 
2. NewJeans - Hype Boy 
3. Ariana Grande - Focus (v)
4. Vance Joy - Saturday Sun (v)
5. Pierce The Veil - Floral & Fading 

CBF_CF

Yuuri - ドライフラワー
1. Yuuri - ドライフラワー (v)
2. Ado - ドライフラワー (v)
3. Tani Yuuki - Aikotoba (v)
4. Tani Yuuki - 愛言葉 (v)
5. ONE OK ROCK - We Are (v)

Lee Mujin - Traffic light(v)
1. KyoungSeo - 120BPM (v)
2. CHEEZE - Mood Indigo 
3. Lee Mujin - Propose (v)
4. BIG Naughty - IMFP 
5. DAY6 (Even of Day) - so this is love 

Ed Sheeran - Galway Girl 
1. Citra Scholastika - Pasti Bisa 
2. NewJeans - Hype Boy 
3. Ariana Grande - Focus (v)
4. Vance Joy - Saturday Sun (v)
5. Pierce The Veil - Floral & Fading 

CF

Yuuri - ドライフラワー
1. SPITZ - 空も飛べるはず 
2. Mrs. GREEN APPLE - Magic (v)
3. Little by Little - 悲しみをやさしさに (v)
4. fromis_9 - Love Me Back 
5. CHiCO with HoneyWorks - 世界は恋に落ちている 

Lee Mujin - Traffic light
1. Lee Sun Hee - Beautiful Landscape (v)
2. Lee Mujin - Episode (v)
3. PATEKO - It's Gone 
4. Lee Mujin - No MBTI 
5. iKON - LOVE SCENARIO 

Ed Sheeran - Galway Girl
1. Jonas Blue - Perfect Strangers (v)
2. Taylor Swift - Love Story (Taylor’s Version) (v)
3. Sean Kingston - Eenie Meenie (v)
4. Carly Rae Jepsen - I Really Like You (v)
5. ZAYN - PILLOWTALK 

CF_CBF

Yuuri - ドライフラワー
1. Mrs. GREEN APPLE - ライラック (v)
2. RADWIMPS - Confession (v)
3. Sukima Switch - 奏(かなで) 
2. Lee Mujin - Traffic light (v)

Lee Mujin - Traffic light
1. Lee Mujin - Propose (v)
2. Lee Mujin - When it snows(Feat.Heize) (v)
3. Alessia Cara - Scars To Your Beautiful 
4. BLACKPINK - PLAYING WITH FIRE 
5. Jay Park - All I Wanna Do (K) (Feat. Hoody & Loco) 

Ed Sheeran - Galway Girl
1. Ed Sheeran - Drunk (v)
2. Ed Sheeran - Barcelona (v)
3. Kygo - It Ain't Me (with Selena Gomez) (v)
4. The Chainsmokers - Paris 
5. Justin Bieber - Love Yourself (v)
"""

if __name__ == "__main__":
    main(data)
