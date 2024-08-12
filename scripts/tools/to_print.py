import re
import os


def process_file(input_path, output_path):
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

    # Combine all the processed blocks
    output = "\n\n".join(results)

    # Write the output to a new file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output)

    print(f"Processed {output_path}")


def process_directory(input_dir, output_dir):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Process each .txt file in the input directory
    for filename in os.listdir(input_dir):
        if filename.endswith('.txt'):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            process_file(input_path, output_path)

    print("Processing complete.")


# Define the input and output directories
input_dir = 'result'
output_dir = 'result/to_recommend'

# Process the directory
process_directory(input_dir, output_dir)
