import re
import os


def process_file(input_path, output_path):
    # Extract the file name without extension for the header
    file_name = os.path.basename(input_path).replace('.txt', '')

    # Read the content of the .txt file
    with open(input_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Initialize a list to hold the results
    results = []

    # Find all instances of SONGS RECOMMENDATION: and their following lines
    pattern = r'(SONGS RECOMMENDATION:.*?)(?=SONGS RECOMMENDATION:|$)'
    blocks = re.findall(pattern, text, re.DOTALL)

    for block in blocks:
        # Extract the header and content
        header_pattern = r'(SONGS RECOMMENDATION:.*?)(?:\n|$)'
        header_match = re.match(header_pattern, block)
        if header_match:
            header = header_match.group(0).strip()
            content = block[len(header):].strip()

            # Find and format the list items
            list_pattern = r'(\d+\. https://open\.spotify\.com/track/\w+ [^\|]+)'
            matches = re.findall(list_pattern, content)

            # Limit the number of entries to 10
            limited_result = matches[:10]

            # Combine header with limited results
            result = f"{header}\n" + "\n".join(limited_result)
            results.append(result)

    # Combine all the processed blocks with the filename header
    output = f"{file_name.upper()}\n\n" + "\n\n".join(results)

    # Write the output to a new file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output)

    # Return the processed output for compilation
    return output


def process_directory(input_dir, output_dir, compiled_file_path):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Initialize a list to store all outputs for the compiled file
    compiled_results = []

    # Process each .txt file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)

            # Process the file and get the output
            file_output = process_file(input_path, output_path)

            # Append the output to the compiled results
            compiled_results.append(file_output)

    # Combine all results and write to the compiled file
    compiled_output = "\n\n".join(compiled_results)
    with open(compiled_file_path, 'w', encoding='utf-8') as compiled_file:
        compiled_file.write(compiled_output)

    print("Processing complete. Compiled file created.")


# Define the input and output directories and the compiled file path
input_dir = 'result'
output_dir = 'result/to_recommend'
compiled_file_path = os.path.join(output_dir, 'compiled.txt')

# Process the directory and create the compiled file
process_directory(input_dir, output_dir, compiled_file_path)
