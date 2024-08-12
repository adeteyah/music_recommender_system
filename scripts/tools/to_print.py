import re

# Read the content of the .txt file into the 'text' variable
with open('result/cf.txt', 'r') as file:
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
    header = re.match(r'(SONGS RECOMMENDATION:)', block).group(0)
    content = block[len(header):]

    # Find and format the list items
    pattern = r'(\d+\. https://open\.spotify\.com/track/\w+ [^|]+)'
    matches = re.findall(pattern, content)

    # Limit the number of entries to 10
    limited_result = matches[:10]

    # Combine header with limited results
    result = f"{header}\n" + "\n".join(limited_result)
    results.append(result)

# Combine all the processed blocks
output = "\n\n".join(results)
print(output)

# Optionally, you can write the output back to a new file
with open('result/to_recommend/cf.txt', 'w') as output_file:
    output_file.write(output)
