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

The Weeknd - Call Out My Name
1. Glee Cast - I'll Stand By You (Glee Cast Version) 
2. Jeon Sang Keun - Love is 
3. Nancy Ajram - Baddi Hada Hebbou 
4. Cocteau Twins - Cico Buff 
5. Jung Yong Hwa - Because I Miss You (Band Ver.) (v)

The Weeknd - One Of The Girls (with JENNIE, Lily Rose Depp)
1. Joji - XNXX 
2. Olivia O'Brien - Josslyn 
3. Trey Songz - Use Somebody - Unplugged 
4. Keenan Nasution - Nuansa Bening 
5. ASTRO - Stay With Me (v)

The Weeknd - Popular (with Playboi Carti & Madonna) - From The Idol Vol. 1 (Music from the HBO Original Series)
1. RAN - Selamat Pagi (v)
2. Kero Kero Bonito - Sick Beat 
3. Matta - Jambu (Janjimu Busuk) (v)
4. Ruby - Leih Beydary Keda 
5. BTS - Anpanman 

CBF_CF

The Weeknd - Call Out My Name
1. Glee Cast - I'll Stand By You (Glee Cast Version) 
2. Jeon Sang Keun - Love is 
3. Nancy Ajram - Baddi Hada Hebbou 
4. Cocteau Twins - Cico Buff 
5. Jung Yong Hwa - Because I Miss You (Band Ver.) (v)

The Weeknd - One Of The Girls (with JENNIE, Lily Rose Depp)
1. Joji - XNXX (v)
2. Olivia O'Brien - Josslyn 
3. Trey Songz - Use Somebody - Unplugged 
4. Keenan Nasution - Nuansa Bening 
5. ASTRO - Stay With Me 

The Weeknd - Popular (with Playboi Carti & Madonna) - From The Idol Vol. 1 (Music from the HBO Original Series)
1. RAN - Selamat Pagi (v)
2. Kero Kero Bonito - Sick Beat 
3. Matta - Jambu (Janjimu Busuk) (v)
4. Ruby - Leih Beydary Keda 
5. ITZY - Cheshire 

CF

The Weeknd - Call Out My Name
1. The Weeknd - Wicked Games (v) 
2. Ariana Grande - Into You (v)
3. Ariana Grande - 34+35 (v)
4. Conan Gray - Memories 
5. Conan Gray - Memories 

The Weeknd - One Of The Girls (with JENNIE, Lily Rose Depp)
1. The Weeknd - Wicked Games (v) 
2. Sabrina Carpenter - Espresso (v)
3. Taylor Swift - Style (v)
4. Taylor Swift - Blank Space (v)
5. Lana Del Rey - Brooklyn Baby 

The Weeknd - Popular (with Playboi Carti & Madonna) - From The Idol Vol. 1 (Music from the HBO Original Series)
1. Sabrina Carpenter - Please Please Please (v)
2. Lana Del Rey - Brooklyn Baby 
3. The Chainsmokers - Closer 
4. Coldplay - A Sky Full of Stars (v)
5. Taylor Swift - Fearless (v)(Taylor’s Version) 

CF_CBF

The Weeknd - Call Out My Name
1. The Weeknd - Is There Someone Else? (V)
2. The Weeknd - Die For You (v)
3. Ariana Grande - Dangerous Woman (v)
4. Bruno Mars - That's What I Like (v)
5. Adele - Someone Like You (v)

The Weeknd - One Of The Girls (with JENNIE, Lily Rose Depp)
1. Arctic Monkeys - Do I Wanna Know? (V)
2. The Neighbourhood - Daddy Issues 
3. Eminem - Mockingbird (v)
4. Kanye West - Runaway 
5. Quavo - Tough 

The Weeknd - Popular (with Playboi Carti & Madonna) - From The Idol Vol. 1 (Music from the HBO Original Series)
1. The Weeknd - Pray For Me (with Kendrick Lamar) (v)
2. Metro Boomin - Creepin' (with The Weeknd & 21 Savage) (v)
3. Ombre2Choc Remix - Unforgettable - Remix 
4. Chase Atlantic - Falling 
5. Lil Mosey - Blueberry Faygo
"""

if __name__ == "__main__":
    main(data)
