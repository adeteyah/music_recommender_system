import re
import os

input_dir = 'result'
output_dir = 'result/to_recommend'
compiled_file_path = os.path.join(output_dir, 'compiled.txt')


def process_file(input_path, output_path):
    file_name = os.path.basename(input_path).replace('.txt', '')
    with open(input_path, 'r', encoding='utf-8') as file:
        text = file.read()

    results = []
    pattern = r'(SONGS RECOMMENDATION:.*?)(?=SONGS RECOMMENDATION:|$)'
    blocks = re.findall(pattern, text, re.DOTALL)

    for block in blocks:
        header_pattern = r'(SONGS RECOMMENDATION:.*?)(?:\n|$)'
        header_match = re.match(header_pattern, block)
        if header_match:
            header = header_match.group(0).strip()
            content = block[len(header):].strip()

            # Find and format the list items
            list_pattern = r'(\d+\. https://open\.spotify\.com/track/\w+ [^|]+)'
            matches = re.findall(list_pattern, content)

            # Remove everything after ' | Genres: ' in the header
            header = re.sub(r'\s*\| Genres:.*', '', header)

            limited_result = matches[:5]
            result = f"{header}\n" + "\n".join(limited_result)
            results.append(result)

    # Add the file name as a header
    output = f"{file_name.upper()}\n\n" + "\n\n".join(results)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output)

    return output


def process_directory():
    os.makedirs(output_dir, exist_ok=True)
    compiled_results = []

    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            file_output = process_file(input_path, output_path)
            compiled_results.append(file_output)

    compiled_output = "\n\n".join(compiled_results)
    with open(compiled_file_path, 'w', encoding='utf-8') as compiled_file:
        compiled_file.write(compiled_output)

    print("Processing complete. Compiled file created.")


# Allow the script to be run independently
if __name__ == "__main__":
    process_directory()
