import re
import os

# Define the input and output directories
input_dir = 'result'
output_dir = 'result/to_recommend'

# Ensure the output directory exists
os.makedirs(output_dir, exist_ok=True)

# Process each .txt file in the input directory
for filename in os.listdir(input_dir):
    if filename.endswith('.txt'):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        # Read the content of the .txt file into the 'text' variable
        with open(input_path, 'r', encoding='utf-8') as file:
            text = file.read()

        # Split the text into separate blocks by using the pattern 'SONGS RECOMMENDATION:'
        blocks = re.split(r'(SONGS RECOMMENDATION:)', text)

        # Initialize a list to hold the results
        results = []

        # Process each block
        for i in range(1, len(blocks), 2):
            # Combine 'SONGS RECOMMENDATION:' with the block content
            block = blocks[i-1] + blocks[i]

            # Extract the SONGS RECOMMENDATION: part
            header = re.search(r'(SONGS RECOMMENDATION:)', block).group(0)
            content = block[len(header):]

            # Find and format the list items
            pattern = r'(\d+\. https://open\.spotify\.com/track/\w+ [^\n]+)'
            matches = re.findall(pattern, content)

            # Debugging: Check if the matches are being captured correctly
            if not matches:
                # Print a snippet of the content for debugging
                print(f"No matches found in block: {content[:200]}")

            # Limit the number of entries to 10
            limited_result = matches[:10]

            # Combine header with limited results
            result = f"{header}\n" + "\n".join(limited_result)
            results.append(result)

        # Combine all the processed blocks
        output = "\n\n".join(results)
        print(f"Processed {filename}")

        # Write the output to a new file
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(output)

print("Processing complete.")
