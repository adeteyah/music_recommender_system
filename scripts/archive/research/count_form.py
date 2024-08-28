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
dapp, yang punya korelasi sama musik yang di kirim kemarin kasih (v) ya di belakang
contoh: 1. artis - judul (v)

CBF

NIKI - Take A Chance With Me
1. NIKI - Take A Chance With Me (v)
2. Faime - Feels Like You (v)
3. NIKI - Pools 
4. Nadhif Basalamah - Something More 
5. Arash Buana - say you're done with me 

John Denver - Take Me Home, Country Roads - Original Version
1. Carpenters - I Won't Last A Day Without You 
2. GoldFord - Walk With Me 
3. Tom Petty and the Heartbreakers - Into The Great Wide Open 
4. Nadya Fatira - Penyendiri 
5. Raisa - Kali Kedua - Acoustic 

Kendrick Lamar - Not Like Us
1. Blu DeTiger - Cotton Candy Lemonade 
2. Joey Bada$$ - FOR MY PEOPLE 
3. J. Cole - No Role Modelz (v)
4. Powfu - The Story of the Paper Boy 
5. Ella Mai - My Way 

CBF_CF

NIKI - Take A Chance With Me
1. NIKI - Take A Chance With Me 
2. Faime - Feels Like You 
3. Nadhif Basalamah - Something More 
4. Arash Buana - say you're done with me (v)
5. Ebony Loren - For The Best 

John Denver - Take Me Home, Country Roads - Original Version
1. Carpenters - I Won't Last A Day Without You 
2. GoldFord - Walk With Me 
3. Tom Petty and the Heartbreakers - Into The Great Wide Open 
4. Nadya Fatira - Penyendiri 
5. HAECHAN - Good Person (2022) 

Kendrick Lamar - Not Like Us
1. Blu DeTiger - Cotton Candy Lemonade 
2. Joey Bada$$ - FOR MY PEOPLE 
3. J. Cole - No Role Modelz 
4. Powfu - The Story of the Paper Boy 
5. Ella Mai - My Way 

CF

NIKI - Take A Chance With Me
1. NIKI - Plot Twist (v)
2. NIKI - Plot Twist 
3. Al James - Atin-Atin Lang 
4. Calein - Umaasa 
5. PinkPantheress - Nineteen 

John Denver - Take Me Home, Country Roads - Original Version
1. Float - Pulang 
2. Hank Locklin - Please Help Me, I'm Falling 
3. Kings of Convenience - Homesick 
4. Captain & Tennille - Do That To Me One More Time 
5. Ed Sheeran - Photograph (v)

Kendrick Lamar - Not Like Us
1. Pop Smoke - What You Know Bout Love 
2. Drake - Passionfruit 
3. Rick Ross - Champagne Moments 
4. Yeat - Poppin 
5. Lil Tecca - LOT OF ME 

CF_CBF

NIKI - Take A Chance With Me
1. NIKI - urs 
2. NIKI - Oceans & Engines 
3. The Cranberries - Linger 
4. Taylor Swift - Guilty as Sin? 
5. Henry Moodie - drunk text 

John Denver - Take Me Home, Country Roads - Original Version
1. ABBA - One Of Us 
2. iKON - RHYTHM TA 
3. Led Zeppelin - Stairway to Heaven - Remaster 
4. Foreigner - I Want to Know What Love Is - 1999 Remaster 
5. Wham! - Wake Me Up Before You Go-Go 

Kendrick Lamar - Not Like Us
1. J. Cole - No Role Modelz 
2. Mustard - Parking Lot 
3. Offset - Ric Flair Drip (& Metro Boomin) 
4. Mustard - Parking Lot 
5. SZA - Nobody Gets Me

Kendrik lamar - not like us
1. Kendrik Lamar -Not like us (v)
2. ⁠john denver - take me home (v)
3. ⁠ Niki - take a chance (v)
"""

if __name__ == "__main__":
    main(data)
