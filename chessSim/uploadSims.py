import gzip
import json
import os

sims = 'chessSim/data/sims/candidates_simulation_results.json.gz'
n_split = 500

# Step 1: Load the gzipped JSON file
def load_gzipped_json(filename):
    with gzip.open(filename, 'rt', encoding='utf-8') as f:
        data = json.load(f)
    return data

# Step 2: Split the document and save into files
def split_and_save(data, path='chessSim/data/sims/split/', num_files=n_split):
    os.makedirs(path, exist_ok=True)  # Ensure the directory exists
    chunk_size = len(data) // num_files
    for i in range(num_files):
        if i % 50 == 0:
            print(f'Processing part {i}...')
        start_index = i * chunk_size
        # Adjust end index to make sure all items are included due to integer division
        end_index = start_index + chunk_size if i < num_files - 1 else len(data)
        part_filename = f'{path}part{str(i).zfill(2)}.json'  # Generates part00, part01, ..., part99
        with open(part_filename, 'w', encoding='utf-8') as f:
            json.dump(data[start_index:end_index], f)

if __name__ == "__main__":

    # # Example usage:
    # data = load_gzipped_json(sims)
    # print(f'Loaded {len(data)} items')

    # split_and_save(data)
    # print(f'Split into {n_split} files')

    # Assuming the files are saved and you're in the same directory
    for i in range(147, n_split):
        print(f'Uploading part {i}...')
        filename = f'chessSim/data/sims/split//part{str(i).zfill(2)}.json'
        os.system(f'./mongoUpload.sh {filename}')