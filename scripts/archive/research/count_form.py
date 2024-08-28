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

    # Output results in the specified order
    for model_name in model_order:
        if model_name in results:
            tps, totals, tp_fp_array = results[model_name]
            print(f"{model_name}:")
            for i, (tp, total) in enumerate(zip(tps, totals)):
                print(
                    f"  Item {i+1}: True Positives = {tp}, Total Recommendations = {total}")
            print(f"  Total Recommendations for {model_name}: {sum(totals)}")
            print(f"  True Positives Array: {tp_fp_array}\n")

    # Total True Positives for each model
    for model_name in model_order:
        if model_name in results:
            tps, totals, tp_fp_array = results[model_name]
            print(f"{model_name}: True Positives (all items) = {
                  tps}, Total Recommendations (all items) = {sum(totals)}")
            print(f"{model_name}: TP/FP Array = {tp_fp_array}")


# Example input
data = """
CBF

JP Saxe - If the World Was Ending (feat. Julia Michaels)
1. The Futurelics - Down N' Out 
2. The Weeknd - True Colors (v)
3. Ed Sheeran - Moving - Bonus Track (v)
4. RealestK - Confessions (v)
5. Sasha Alex Sloan - Dancing With Your Ghost (v)

Yahya - keepyousafe
1. Yahya - keepyousafe (v)
2. Jinan Laetitia - POV 
3. Skyline - How Do You Heal a Broken Heart? (v) 
4. Jan Metternich archive - Supermarket Flowers - Acoustic Version 
5. Noni - Things I Could Never Say to You (v)

One Direction - Night Changes
1. Deborah Cox - Nobody's Supposed to Be Here 
2. Jaden - BYE (v)
3. Plastic Plastic - With Me 
4. PVRIS - Death of Me 
5. Daniel Bedingfield - If You're Not The One (v)

CBF_CF

JP Saxe - If the World Was Ending (feat. Julia Michaels)
1. The Futurelics - Down N' Out 
2. The Weeknd - True Colors (v)
3. RealestK - Confessions (v)
4. Sasha Alex Sloan - Dancing With Your Ghost 
5. Drow$y - Under The Pipes (v)

Yahya - keepyousafe
1. Yahya - keepyousafe (v)
2. Jinan Laetitia - POV 
3. Skyline - How Do You Heal a Broken Heart? 
4. Jan Metternich archive - Supermarket Flowers - Acoustic Version 
5. Noni - Things I Could Never Say to You (v)

One Direction - Night Changes
1. Deborah Cox - Nobody's Supposed to Be Here 
2. Jaden - BYE (v)
3. Plastic Plastic - With Me 
4. PVRIS - Death of Me (v)
5. Daniel Bedingfield - If You're Not The One (v)

CF

JP Saxe - If the World Was Ending (feat. Julia Michaels)
1. Gabrielle Aplin - Please Don't Say You Love Me (v)
2. Ardhito Pramono - I Just Couldn't Save You Tonight - Story of Kale - Original Motion Picture Soundtrack (v)
3. Cody Fry - I Hear a Symphony 
4. Genevieve Stokes - Habits 
5. Cigarettes After Sex - K. (v)

Yahya - keepyousafe
1. Isyana Sarasvati - Heaven (v)
2. Kurosuke - Fantasy 
3. Ardhito Pramono - I Just Couldn't Save You Tonight - Story of Kale - Original Motion Picture Soundtrack (v)
4. Sal Priadi - Bulan Yang Baik 
5. NIKI - La La Lost You - Acoustic Version (v)

One Direction - Night Changes
1. Isyana Sarasvati - Heaven 
2. Tulus - Monokrom (v)
3. Sickick - Mind Games 
4. Idgitaf - Takut (v)
5. The Lumineers - Ho Hey 

CF_CBF

JP Saxe - If the World Was Ending (feat. Julia Michaels)
1. BANNERS - Someone To You (v)
2. The Lumineers - Ophelia 
3. The Walters - I Love You So (v)
4. Cody Fry - I Hear a Symphony (v)
5. Ariana Grande - supernatural (v)

Yahya - keepyousafe
1. Olivia Rodrigo - enough for you (v)
2. Jung Kook - Still With You (v)
3. Isyana Sarasvati - Heaven (v)
4. Lana Del Rey - Born To Die 
5. Sal Priadi - Bulan Yang Baik 

One Direction - Night Changes
1. One Direction - Right Now (v)
2. One Direction - Story of My Life (v)
3. 5 Seconds of Summer - Youngblood 
4. Billie Eilish - Bored 
5. Harry Styles - Sign of the Times
"""

if __name__ == "__main__":
    main(data)
