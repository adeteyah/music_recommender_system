import os

# Path to the directory containing the CSV files
directory_path = r"C:\\Users\\Adeteyah\\Documents\\hybrid_music_recommendation\\data\\raw"
output_directory = r"C:\Users\Adeteyah\Documents\music_recommender_system\data"

# Ensure the output directory exists
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Set to store unique IDs
unique_ids = set()

# Iterate over all files in the directory
for filename in os.listdir(directory_path):
    if filename.endswith(".csv"):
        unique_id = filename.split('_')[0]
        unique_ids.add(unique_id)

# Convert the set to a list
unique_ids_list = list(unique_ids)

# Function to split list into chunks


def split_list(lst, chunk_size):
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


# Split the list into chunks of 500 IDs each
chunks = list(split_list(unique_ids_list, 500))

# Save each chunk to a separate text file
for idx, chunk in enumerate(chunks, start=1):
    output_path = os.path.join(output_directory, f'unique_ids_chunk_{idx}.txt')
    with open(output_path, 'w') as f:
        # Write the array format to the file
        f.write(str(chunk).replace("'", '"'))

    print(f'Chunk {idx} saved to {output_path}')
