import re
import os


def consolidate_ids(text):
    # Define the pattern to find INPUTTED IDS and their following items
    pattern = r'(INPUTTED IDS\s*[\s\S]*?)(?=INPUTTED IDS\s|$)'
    blocks = re.findall(pattern, text)

    consolidated_result = []

    for block in blocks:
        # Find and number items within each INPUTTED IDS block
        item_pattern = r'(\d+\.)\s+([^\n]+)'
        items = re.findall(item_pattern, block)

        # Create the new consolidated block
        if items:
            consolidated_block = 'INPUTTED IDS'
            for idx, (number, item) in enumerate(items, start=1):
                consolidated_block += f'\n{idx}. {item}'
            consolidated_result.append(consolidated_block)

    return '\n\n'.join(consolidated_result)


def process_file(input_path, output_path):
    # Read the content of the .txt file
    with open(input_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Consolidate the INPUTTED IDS blocks
    consolidated_text = consolidate_ids(text)

    # Write the consolidated text to a new file
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(consolidated_text)

    print(f"Processed {input_path}")


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
