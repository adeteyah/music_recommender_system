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

SONGS RECOMMENDATION: https://open.spotify.com/track/7ovUcF5uHTBRzUpB6ZOmvt BABYMONSTER - SHEESH
1. https://open.spotify.com/track/5uTprTAUORprODnl383LKx NCT 127 - Fly Away With Me 
2. https://open.spotify.com/track/55UNoOCjEO5EvDpmSJQN76 iKON - LONG TIME NO SEE 
3. https://open.spotify.com/track/30VA0uReR9jKiFU7ddriN6 STAYC - LOVE (v)
4. https://open.spotify.com/track/2e3cJdJ8xWwydl8JIYlCqB WayV - Love Talk - English Version (v)
5. https://open.spotify.com/track/6oEf7aR2iXAVbRG76bE9nQ Lone Tusker - Little While 

SONGS RECOMMENDATION: https://open.spotify.com/track/0ZSjUIhmsXaa9Vq7DfXCKL aespa - Supernova
1. https://open.spotify.com/track/2VdSktBqFfkW7y6q5Ik4Z4 aespa - Supernova (v)
2. https://open.spotify.com/track/3aGqHdZJusdhT3ZzfLRnO7 ITZY - KIDDING ME (v)
3. https://open.spotify.com/track/6bvZRLLkBKkmgpBJTTj3QK BLACKPINK - How You Like That (v) 
4. https://open.spotify.com/track/7HGKvoju3ucB7UqVt1GoJu STAYC - YOUNG LUV 
5. https://open.spotify.com/track/1nMbZ9OsVNSLEyijI80EST TWICE - TT (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/7mYwDmbbp8UPLlnRjTJ54X YOASOBI - アイドル
1. https://open.spotify.com/track/1HHFCfMYMnCXM8T3iofubG Ado - 可愛くてごめん (v)
2. https://open.spotify.com/track/4Z8WSP6i30vg05WTDyvw0X ヨルシカ - あの夏に咲け 
3. https://open.spotify.com/track/45Qz90khfSW8AnaH9vNg5j RADWIMPS - 05410-(ん) 
4. https://open.spotify.com/track/2XpV9sHBexcNrz0Gyf3l18 Ikimonogakari - ブルーバード 
5. https://open.spotify.com/track/7ntInJEUj7yhOYVFLLKK4t AKB48 - Seventeen

CBF_CF

SONGS RECOMMENDATION: https://open.spotify.com/track/1njlnn8ZKHI77Pe9szIONR BABYMONSTER - SHEESH
1. https://open.spotify.com/track/0UzymivvUH5s8z4PeWZJaK ENHYPEN - FEVER (v)
2. https://open.spotify.com/track/4dtmj7X21gunWoQf98hW5L Aisha Retno - W.H.U.T 
3. https://open.spotify.com/track/6CdUgvL597jWmW4w8P5kHs TAEYEON - Fine 
4. https://open.spotify.com/track/5xwBIieMMFUmLDgvG4DjFe Stacey Ryan - Fall In Love Alone 
5. https://open.spotify.com/track/3VBj0lzjmhTzVFPEDOjNCG BABYMONSTER - BATTER UP (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/18nZWRpJIHzgb1SQr4ncwb aespa - Supernova
1. https://open.spotify.com/track/65FftemJ1DbbZ45DUfHJXE NewJeans - OMG (v)
2. https://open.spotify.com/track/0Q5VnK2DYzRyfqQRJuUtvi IVE - LOVE DIVE (v)
3. https://open.spotify.com/track/618OKP1lBkNJL8uZdNSvQE VIVIZ - MANIAC (vvvvv)
4. https://open.spotify.com/track/24nK8tW7Pt3Inh2utttuoG MAMAMOO - HIP (v)
5. https://open.spotify.com/track/1t8sqIScEIP0B4bQzBuI2P (G)I-DLE - MY BAG (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/7ovUcF5uHTBRzUpB6ZOmvt YOASOBI - アイドル
1. https://open.spotify.com/track/2XpV9sHBexcNrz0Gyf3l18 Ikimonogakari - ブルーバード 
2. https://open.spotify.com/track/2jdbZGFp8KVTuk0YxDNL4l back number - 高嶺の花子さん 
3. https://open.spotify.com/track/3wJHCry960drNlAUGrJLmz ヨルシカ - ただ君に晴れ 
4. https://open.spotify.com/track/1zd35Y44Blc1CwwVbW3Qnk YOASOBI - 群青 (v)
5. https://open.spotify.com/track/45YBVp6zMwQZRbUDcPzmMB Kenshi Yonezu - アイネクライネ (v)

CF

SONGS RECOMMENDATION: https://open.spotify.com/track/1njlnn8ZKHI77Pe9szIONR BABYMONSTER - SHEESH
1. https://open.spotify.com/track/3VBj0lzjmhTzVFPEDOjNCG BABYMONSTER - BATTER UP (v)
2. https://open.spotify.com/track/5XWlyfo0kZ8LF7VSyfS4Ew aespa - Drama (v)
3. https://open.spotify.com/track/1aKvZDoLGkNMxoRYgkckZG ILLIT - Magnetic (v)
4. https://open.spotify.com/track/0vaxYDAuAO1nPolC6bQp7V KISS OF LIFE - Midas Touch (v)
5. https://open.spotify.com/track/74X2u8JMVooG2QbjRxXwR8 LE SSERAFIM - Perfect Night (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/18nZWRpJIHzgb1SQr4ncwb aespa - Supernova
1. https://open.spotify.com/track/38tXZcL1gZRfbqfOG0VMTH NewJeans - How Sweet 
2. https://open.spotify.com/track/5XWlyfo0kZ8LF7VSyfS4Ew aespa - Drama (v)
3. https://open.spotify.com/track/1aKvZDoLGkNMxoRYgkckZG ILLIT - Magnetic (v)
4. https://open.spotify.com/track/3VBj0lzjmhTzVFPEDOjNCG BABYMONSTER - BATTER UP (v)
5. https://open.spotify.com/track/7uyeEbG6hyApgXuEypGcsZ IVE - Baddie 

SONGS RECOMMENDATION: https://open.spotify.com/track/7ovUcF5uHTBRzUpB6ZOmvt YOASOBI - アイドル
1. https://open.spotify.com/track/3dPtXHP0oXQ4HCWHsOA9js YOASOBI - 夜に駆ける (v)
2. https://open.spotify.com/track/51oc6MEsXTpnPn6GOw5VuP Fujii Kaze - きらり (v)
3. https://open.spotify.com/track/0F6nGXMCUbtk8FiXvKi6HK 『ユイカ』 - 好きだから。 
4. https://open.spotify.com/track/6nqfKM9JvQIiuAuzWZFvGW もさを。 - ぎゅっと。 
5. https://open.spotify.com/track/2Dzzhb1oV5ckgOjWZLraIB natori - Overdose (v)

CF_CBF

SONGS RECOMMENDATION: https://open.spotify.com/track/1njlnn8ZKHI77Pe9szIONR BABYMONSTER - SHEESH
1. https://open.spotify.com/track/3VBj0lzjmhTzVFPEDOjNCG BABYMONSTER - BATTER UP (v)
2. https://open.spotify.com/track/1aKvZDoLGkNMxoRYgkckZG ILLIT - Magnetic (v)
3. https://open.spotify.com/track/2O4Bb2WCkjlTPO827OnBMI LE SSERAFIM - EASY (v)
4. https://open.spotify.com/track/5sdQOyqq2IDhvmx2lHOpwd NewJeans - Super Shy (v)
5. https://open.spotify.com/track/7uyeEbG6hyApgXuEypGcsZ IVE - Baddie 

SONGS RECOMMENDATION: https://open.spotify.com/track/18nZWRpJIHzgb1SQr4ncwb aespa - Supernova
1. https://open.spotify.com/track/74X2u8JMVooG2QbjRxXwR8 LE SSERAFIM - Perfect Night (v)
2. https://open.spotify.com/track/7uyeEbG6hyApgXuEypGcsZ IVE - Baddie 
3. https://open.spotify.com/track/6zZWoHlF2zNSLUNLvx4GUl aespa - Better Things (v)
4. https://open.spotify.com/track/34pKV56b6d7Nz1l6av1nZ1 (G)I-DLE - I Want That (v)
5. https://open.spotify.com/track/3v5o91PrUtf0nmO6j8J7dZ XG - LEFT RIGHT (v)

SONGS RECOMMENDATION: https://open.spotify.com/track/7ovUcF5uHTBRzUpB6ZOmvt YOASOBI - アイドル
1. https://open.spotify.com/track/1zd35Y44Blc1CwwVbW3Qnk YOASOBI - 群青 (v)
2. https://open.spotify.com/track/5Yiwmn4PZAzVAms9UDICU2 物語シリーズ - 白金ディスコ 
3. https://open.spotify.com/track/7GoPAWftpQzN8euEs2mgM6 Tani Yuuki - おかえり 
4. https://open.spotify.com/track/10zz9RZt9DnqcxNWksRNrx Vaundy - 怪獣の花唄 
5. https://open.spotify.com/track/4NaaF28BeO9WzjDrSS71Nz Mrs. GREEN APPLE - ダンスホール
"""

if __name__ == "__main__":
    main(data)
