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

Dhika Fawaz - Hilmira
1. Dimas M - Sekarang Hingga Nanti Kita Tua 
2. Hanin Dhiya - Pupus (v) 
3. Nathaniel Constantin - Why Can't I 

Mocca - Let Me Go
1. Theresia Margaretha Gultom - Tanah Airku 
2. Arash Buana - i'll be friend's with you - phone recorded (v) 
3. Mikha Angelo - Amateur (v) 
4. Yura Yunita - Tutur Batin (v) 
5. Sal Priadi - Episode 

Endah N Rhesa - Wish You Were Here
1. Liv Harland - What a Lie 
2. Elephant Kind - Something Better (v) 
3. Danilla - Wahai Kau 
4. Tarasinta - Summer in France 
5. Rendy Pandugo - Hampir Sempurna (v) 

CBF_CF

Dhika Fawaz - Hilmira
1. Dimas M - Sekarang Hingga Nanti Kita Tua 
2. Hanin Dhiya - Pupus (v) 
3. Nathaniel Constantin - Why Can't I 
4. Mikha Angelo - Amateur 
5. Chrisye - Kisah Kasih Di Sekolah 

Mocca - Let Me Go
1. Theresia Margaretha Gultom - Tanah Airku 
2. Arash Buana - i'll be friend's with you - phone recorded (v) 
3. Mikha Angelo - Amateur (v) 
4. Yura Yunita - Tutur Batin (v) 
5. Sal Priadi - Episode 

Endah N Rhesa - Wish You Were Here
1. Liv Harland - What a Lie 
2. Elephant Kind - Something Better (v) 
3. Danilla - Wahai Kau 
4. Tarasinta - Summer in France 
5. Rendy Pandugo - Hampir Sempurna (v)

CF

Dhika Fawaz - Hilmira
1. Tulus - Teman Hidup 
2. Hindia - Evaluasi (Reprise) 
3. Tulus - Hati-Hati di Jalan (v)
4. Nadin Amizah - Taruh (v)
5. Feby Putri - Halu (v)

Mocca - Let Me Go
1. Deredia - Kisah Mencari Seorang Raja 
2. Vira Talisa - He's Got Me Singing Again 
3. Danilla - Reste Avec Moi (v)
4. Mocca - Ketika Semua Telah Berakhir (v)
5. Isyana Sarasvati - Luruh (v)

Endah N Rhesa - Wish You Were Here
1. Endah N Rhesa - Ssslow (v)
2. Danilla - Reste Avec Moi (v)
3. Kunto Aji - Rehat 
4. Kunto Aji - Rehat 
5. Daramuda - Growing Up (Rara Sekar) 

CF_CBF

Dhika Fawaz - Hilmira
1. Rendy Pandugo - By My Side 
2. Mocca - Let Me Go (v)

Mocca - Let Me Go
3. Endah N Rhesa - Wish You Were Here (v) 

Endah N Rhesa - Wish You Were Here
1. Figura Renata - Hingga Tenang 
2. Matter Halo - Travel (v)
3. Danilla - Wahai Kau (v)
"""

if __name__ == "__main__":
    main(data)
