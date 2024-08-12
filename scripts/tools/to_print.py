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

    # Use re to find and remove everything after the song title
    pattern = r'(SONGS RECOMMENDATION: https://open\.spotify\.com/track/\w+ [^|]+)|(\d+\. https://open\.spotify\.com/track/\w+ [^|]+)'
    matches = re.findall(pattern, block)

    # Format the matches
    result = []
    for match in matches:
        song_recommendation = match[0].strip(
        ) if match[0] else match[1].strip()
        result.append(song_recommendation)

    # Limit the number of entries to 10
    limited_result = result[:10]

    # Join the results into a single string
    results.append("\n".join(limited_result))

# Combine all the processed blocks
output = "\n\n".join(results)
print(output)

# Optionally, you can write the output back to a new file
with open('output.txt', 'w') as output_file:
    output_file.write(output)
