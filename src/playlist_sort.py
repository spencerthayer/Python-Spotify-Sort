import json
import pandas as pd
import os
import re

def setup_directories():
    """Ensure necessary directories exist and return the data directory path."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    data_dir = os.path.join(script_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    return data_dir

def load_weights(data_dir):
    """Load weights from JSON file."""
    with open(os.path.join(data_dir, 'playlists.json'), 'r') as json_file:
        data = json.load(json_file)
    return data.get('weights', {})  # Return only the 'weights' sub-dictionary


def circle_of_fifths_distance(key1, mode1, key2, mode2):
    """Calculate the Circle of Fifths distance between two keys."""
    major_keys = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
    minor_keys = [(k + 3) % 12 for k in major_keys]
    key1_circle = major_keys[key1] if mode1 == 1 else minor_keys[key1]
    key2_circle = major_keys[key2] if mode2 == 1 else minor_keys[key2]
    return min(abs(key1_circle - key2_circle), 12 - abs(key1_circle - key2_circle))

def calculate_sort_score(row, df, weights):
    score = 0
    for feature in ['energy', 'tempo', 'key', 'mode']:
        weight = weights.get(feature, 0)  # Use get method with default 0
        if weight > 0:  # Process only if weight is greater than 0
            if feature in ['key', 'mode']:
                row_key = int(row['key']) if not pd.isna(row['key']) else 0
                row_mode = int(row['mode']) if not pd.isna(row['mode']) else 0
                differences = df.apply(lambda x: circle_of_fifths_distance(row_key, row_mode, int(x['key']), int(x['mode'])), axis=1)
            else:
                differences = abs(df[feature] - row[feature])
            feature_score = weight * differences.sum()
            score += feature_score
    return score

def assign_new_order(df):
    """Assign a unique new order to each DataFrame row."""
    df['new_order'] = range(len(df))
    return df

def main():
    data_dir = setup_directories()
    playlist_weights = load_weights(data_dir)

    input_file = os.path.join(data_dir, 'playlist_features.csv')

    try:
        features_df = pd.read_csv(input_file)
    except FileNotFoundError:
        print(f"Error: File {input_file} not found.")
        return

    # Convert 'key' and 'mode' to numeric values, handling errors
    features_df['key'] = pd.to_numeric(features_df['key'], errors='coerce')
    features_df['mode'] = pd.to_numeric(features_df['mode'], errors='coerce')

    # Additional debugging: Checking data types and value ranges
    print("Data types:\n", features_df.dtypes)
    print("Value ranges:\n", features_df.describe())

    # Calculate sort scores
    features_df['sort_score'] = features_df.apply(lambda row: calculate_sort_score(row, features_df, playlist_weights), axis=1)

    # Debugging: Print sample sort scores
    print("Sample calculated sort scores:\n", features_df['sort_score'].head())

    # Sorting the playlist based on the calculated scores
    sorted_playlist = features_df.sort_values(by='sort_score', ascending=True).reset_index(drop=True)

    # Assigning a new order to the sorted playlist
    sorted_playlist = assign_new_order(sorted_playlist)

    # Debugging: Print DataFrame after sorting and the final sorted playlist
    print("DataFrame before sorting:\n", features_df.head())
    print("DataFrame after sorting:\n", sorted_playlist.head())
    print("Final sorted playlist with new order:\n", sorted_playlist.head())

    # Saving the sorted playlist to a CSV file
    output_file = os.path.join(data_dir, 'playlist_sorted.csv')
    sorted_playlist.to_csv(output_file, index=False)
    print(f'Playlist sorted and saved to {output_file}')

if __name__ == '__main__':
    main()
