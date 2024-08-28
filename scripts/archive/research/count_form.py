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
piw, yang punya korelasi sama musik yang di kirim kemarin kasih (v) ya di belakang
contoh: 1. artis - judul (v)

CBF

My Chemical Romance - Disenchanted (v)
1. Dashboard Confessional - Stolen 
2. The Script - For the First Time 
3. Marilyn Manson - They Said That Hell's Not Hot 
4. ONE OK ROCK - Wherever you are (v)
5. Sunday (1994) - Tired Boy 

Bon Jovi - It's My Life (v)
1. Hippo Campus - Way It Goes 
2. Marilyn Manson - Cupid Carries A Gun 
3. Sylvan Esso - Radio 
4. Twenty One Pilots - We Don't Believe What's on TV (v)
5. The Cure - The End Of The World 

Avenged Sevenfold - A Little Piece of Heaven
1. Avenged Sevenfold - A Little Piece of Heaven (v)
2. Falling In Reverse - The Drug In Me Is You 
3. Foo Fighters - DOA (v)
4. 311 - Whiskey And Wine 
5. Mike Repic - Alive 

CBF_CF

My Chemical Romance - Disenchanted
1. Dashboard Confessional - Stolen 
2. The Script - For the First Time 
3. Marilyn Manson - They Said That Hell's Not Hot 
4. ONE OK ROCK - Wherever you are (v)
5. Sunday (1994) - Tired Boy 

Bon Jovi - It's My Life
1. Hippo Campus - Way It Goes 
2. Marilyn Manson - Cupid Carries A Gun 
3. Sylvan Esso - Radio 
4. Twenty One Pilots - We Don't Believe What's on TV 
5. The Cure - The End Of The World 

Avenged Sevenfold - A Little Piece of Heaven
1. Avenged Sevenfold - A Little Piece of Heaven 
2. Falling In Reverse - The Drug In Me Is You 
3. Foo Fighters - DOA 
4. 311 - Whiskey And Wine 
5. Mike Repic - Alive 

CF

My Chemical Romance - Disenchanted
1. AC/DC - Girls Got Rhythm (v)
2. Three Days Grace - Never Too Late 
3. Bring Me The Horizon - Doomed (v)
4. Deftones - Change (In the House of Flies) 
5. Bring Me The Horizon - sugar honey ice & tea 

Bon Jovi - It's My Life
1. Bring Me The Horizon - Doomed 
2. Bring Me The Horizon - sugar honey ice & tea 
3. Bon Jovi - Runaway 
4. The Cure - Lovesong 
5. Nirvana - About A Girl 

Avenged Sevenfold - A Little Piece of Heaven
1. Green Day - 21 Guns (v)
2. The Cure - Boys Don't Cry 
3. Avenged Sevenfold - So Far Away (v)
4. Arctic Monkeys - When The Sun Goes Down 
5. Oasis - Wonderwall (v)

CF_CBF

My Chemical Romance - Disenchanted
1. My Chemical Romance - The End. (V)
2. Oasis - Wonderwall - Remastered 
3. Paramore - Misery Business (v)
4. Lord Huron - The Night We Met 
5. Coldplay - Yellow (v)

Bon Jovi - It's My Life
1. Green Day - Last Night on Earth (v)
2. Guns N' Roses - Patience (v)
3. Aerosmith - I Don't Want to Miss a Thing - From "Armageddon" Soundtrack (v)
4. Nirvana - Come As You Are 
5. Queen - Radio Ga Ga - Live Aid (v)

Avenged Sevenfold - A Little Piece of Heaven
1. Avenged Sevenfold - 4:00 AM 
2. Mr. Big - Wild World - 2009 Remastered Version 
3. Liam Gallagher - For What It's Worth 
4. Slipknot - Duality (v)
"""

if __name__ == "__main__":
    main(data)
