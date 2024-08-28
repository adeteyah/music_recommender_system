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
xenn, yang punya korelasi sama musik yang di kirim kemarin kasih (v) ya di belakang
contoh: 1. artis - judul (v)

CBF

Aimer - カタオモイ
1. Aimer - カタオモイ (v)
2. Vaundy - 東京フラッシュ 
3. 이경섭 - Title 허밍 
4. eldon - Pink cheeks 
5. ヨルシカ - ブレーメン 

Juicy Luicy - Jemari
1. HAECHAN - Good Person (2022) 
2. Nadya Fatira - Penyendiri 
3. Raisa - Kali Kedua - Acoustic 
4. Katie - Yang Telah Merelakanmu X Jaga Selalu Hatimu 
5. Slank - Terbunuh Sepi 

Lewis Capaldi - Before You Go
1. Lewis Capaldi - Before You Go (v)
2. Hawthorne Heights - Niki Fm 
3. Ada Band - Yang Terbaik Bagimu 
4. Ada Band - Yang Terbaik Bagimu - Jangan Lupakan Ayah 
5. Rex Orange County - Apricot Princess 

CBF_CF

Aimer - カタオモイ
1. Aimer - カタオモイ (v)
2. Vaundy - 東京フラッシュ 
3. 이경섭 - Title 허밍 
4. eldon - Pink cheeks 
5. ヨルシカ - ブレーメン 

Juicy Luicy - Jemari
1. HAECHAN - Good Person (2022) 
2. Nadya Fatira - Penyendiri 
3. Katie - Yang Telah Merelakanmu X Jaga Selalu Hatimu 
4. Slank - Terbunuh Sepi 
5. Dere - Rumah 

Lewis Capaldi - Before You Go
1. Lewis Capaldi - Before You Go (v)
2. Hawthorne Heights - Niki Fm 
3. Ada Band - Yang Terbaik Bagimu 
4. Ada Band - Yang Terbaik Bagimu - Jangan Lupakan Ayah 
5. Rex Orange County - Apricot Princess 

CF

Aimer - カタオモイ
1. ヨルシカ - 花に亡霊 
2. Yuuri - ミズキリ-piano ver.- 
3. Motohiro Hata - ひまわりの約束 (v)
4. YOASOBI - たぶん (v)
5. Yuuri - レオ 

Juicy Luicy - Jemari
1. Hindia - Setengah Tahun Ini 
2. Juicy Luicy - Tanpa Tergesa (v) 
3. Lalahuta - 1 2 3 
4. Hindia - Besok Mungkin Kita Sampai 
5. Yovie Widianto - Mantan Terindah 

Lewis Capaldi - Before You Go
1. James Arthur - Say You Won't Let Go (v)
2. Freddie Mercury - Love Me Like There's No Tomorrow - Special Edition 
3. Maroon 5 - Memories (v)
4. Sam Smith - Stay With Me (v)
5. Maroon 5 - Memories (v)

CF_CBF

Aimer - カタオモイ
1. Fujii Kaze - Matsuri (v)
2. Ado - ギラギラ 
3. Mrs. GREEN APPLE - 私は最強 
4. Tate McRae - stupid 
5. Daoko - 打上花火 

Juicy Luicy - Jemari
1. Juicy Luicy - Kembali Kesepian 
2. Juicy Luicy - H-5 
3. Rossa - Aku Bukan Untukmu 
4. Fatin - Salahkah Aku Terlalu Mencintaimu 
3. Lewis Capaldi - Before You Go (v)

Lewis Capaldi - Before You Go
1. Lewis Capaldi - Bruises 
2. Conan Gray - Memories (v)
3. Niall Horan - This Town (v)
4. Bazzi - Why 
5. Lana Del Rey - Summertime Sadness (v)
"""

if __name__ == "__main__":
    main(data)
