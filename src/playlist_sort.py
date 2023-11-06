import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.utils import shuffle
import os

# Ensure the directory exists
os.makedirs(os.path.dirname('../data/'), exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the data directory
data_dir = os.path.join(script_dir, '..', 'data')

def enhanced_nearest_neighbor_sort(features_df):
    # Shuffle the DataFrame to remove any bias due to initial ordering
    shuffled_df = shuffle(features_df, random_state=42).reset_index(drop=True)
    features = shuffled_df[['danceability', 'energy', 'key', 'loudness', 'mode', 
                            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']].values
    distances = euclidean_distances(features)

    # Enhanced nearest neighbor sort: considering all possible starting points
    best_length = np.inf
    best_path = []

    for start_index in range(len(features)):
        current_index = start_index
        path = [current_index]
        length = 0

        for i in range(len(features) - 1):
            remaining_indices = np.setdiff1d(np.arange(len(features)), path)
            next_index = remaining_indices[np.argmin(distances[current_index, remaining_indices])]
            length += distances[current_index, next_index]
            path.append(next_index)
            current_index = next_index

        # Check if the current path is the shortest one found so far
        if length < best_length:
            best_length = length
            best_path = path

    # Reorder the original DataFrame according to the best path found
    sorted_df = features_df.iloc[best_path].reset_index(drop=True)
    # Add a 'new_order' column representing the new order
    sorted_df['new_order'] = np.arange(1, len(sorted_df) + 1)
    return sorted_df

def main():
    # Load the playlist features from the CSV file
    input_file = os.path.join(data_dir, 'playlist_features.csv')
    features_df = pd.read_csv(input_file)
    
    # Run the enhanced nearest neighbor sort
    sorted_playlist = enhanced_nearest_neighbor_sort(features_df)
    
    # Save the sorted playlist to a new CSV file
    output_file = os.path.join(data_dir, 'playlist_sorted.csv')
    sorted_playlist.to_csv(output_file, index=False)
    
    print('Playlist sorted and saved to', output_file)

if __name__ == '__main__':
    main()
