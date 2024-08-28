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

Doja Cat - Agora Hills
1. Daya - Insomnia (v)
2. Ofenbach - Be Mine 
3. Michael Bublé - Everything 
4. Isyana Sarasvati - Cinta Pertama 
5. Kaskade - Atmosphere 

Redbone - Come and Get Your Love - Single Version
1. Redbone - Come and Get Your Love 
2. Link Wray - Fire And Brimstone 

Electric Light Orchestra - Mr. Blue Sky
1. Electric Light Orchestra - Mr. Blue Sky 
2. Billy Joel - Piano Man (v)
3. Secondhand Serenade - Fall for You (Acoustic) 
4. Geisha - Remuk Jantungku 
5. Slank - Bali Bagus 

CBF_CF

Doja Cat - Agora Hills
1. Daya - Insomnia 
2. Ofenbach - Be Mine 
3. Michael Bublé - Everything 
4. Isyana Sarasvati - Cinta Pertama 
5. Kaskade - Atmosphere 

Redbone - Come and Get Your Love - Single Version
1. Redbone - Come and Get Your Love 
2. Link Wray - Fire And Brimstone 

Electric Light Orchestra - Mr. Blue Sky
1. Electric Light Orchestra - Mr. Blue Sky 
2. Billy Joel - Piano Man 
3. Secondhand Serenade - Fall for You (Acoustic) 
4. Geisha - Remuk Jantungku 
5. Slank - Bali Bagus 

CF

Doja Cat - Agora Hills
1. The Weeknd - Is There Someone Else? 
2. Chase Atlantic - Friends 
3. Lana Del Rey - West Coast 
4. Kanii - I Know - PR1SVX Edit (v)
5. Brent Faiyaz - ALL MINE 

Redbone - Come and Get Your Love - Single Version
1. The Runaways - Cherry Bomb 
2. Ram Jam - Black Betty 
3. khai dreams - Sunkissed 
4. Neil Diamond - Cracklin' Rosie (v)
5. Jason Mraz - I'm Yours 

Electric Light Orchestra - Mr. Blue Sky
1. Spandau Ballet - Gold 
2. Tsuko G. - Deja Vu (Initial D) 
3. The Beatles - Day Tripper - Remastered 2015 (v)
4. Kylie Minogue - Can't Get You out of My Head 
5. The Runaways - Cherry Bomb 

CF_CBF

Doja Cat - Agora Hills
1. Doja Cat - Ain't Shit 
2. Lana Del Rey - West Coast 
3. The Neighbourhood - Sweater Weather 
4. Megan Thee Stallion - Sweetest Pie 
5. Selena Gomez - Fetish (feat. Gucci Mane) 

Redbone - Come and Get Your Love - Single Version
1. Redbone - Come and Get Your Love 
2. No Doubt - Just A Girl 
3. Dexys Midnight Runners - Come On Eileen 
4. Marvin Gaye - Trouble Man 
5. Zedd - The Middle 

Electric Light Orchestra - Mr. Blue Sky
1. Creedence Clearwater Revival - Bad Moon Rising 
2. Ramones - Blitzkrieg Bop - 2016 Remaster 
3. Billy Joel - Piano Man 
4. The Brook & The Bluff - Halfway Up 
5. The Beatles - Norwegian Wood (This Bird Has Flown) - Remastered 2009
"""

if __name__ == "__main__":
    main(data)
