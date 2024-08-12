import re

# Read the content of the .txt file into the 'text' variable
with open('result/cf.txt', 'r') as file:
    text = file.read()

# Use re to find and remove everything after the song title
pattern = r'(SONGS RECOMMENDATION: https://open\.spotify\.com/track/\w+ [^|]+)|(\d+\. https://open\.spotify\.com/track/\w+ [^|]+)'
matches = re.findall(pattern, text)

# Format the matches
result = []
for match in matches:
    song_recommendation = match[0].strip() if match[0] else match[1].strip()
    result.append(song_recommendation)

# Limit the number of entries to 10
limited_result = result[:10]

# Join the results into a single string
output = "\n".join(limited_result)
print(output)

# Optionally, you can write the output back to a new file
with open('output.txt', 'w') as output_file:
    output_file.write(output)
