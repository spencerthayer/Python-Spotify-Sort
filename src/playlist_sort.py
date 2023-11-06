import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
import os

def nearest_neighbor_sort(features_df):
    # Extracting feature values
    features = features_df[['danceability', 'energy', 'key', 'loudness', 'mode', 
                            'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo']].values

    # Compute distance matrix
    distances = euclidean_distances(features)

    # Start from the first track
    current_index = 0
    path = [current_index]

    # Nearest neighbor algorithm
    for i in range(len(features) - 1):
        remaining_indices = np.setdiff1d(np.arange(len(features)), path)
        next_index = remaining_indices[np.argmin(distances[current_index, remaining_indices])]
        path.append(next_index)
        current_index = next_index

    sorted_df = features_df.iloc[path].reset_index(drop=True)
    return sorted_df

def main():
    print("Sorting playlist...")

    # Load track features
    input_file = os.path.join('../data', 'playlist_features.csv')
    playlist_features = pd.read_csv(input_file)

    # Sort tracks using nearest neighbor algorithm
    sorted_playlist = nearest_neighbor_sort(playlist_features)

    # Add a new_order column to represent the new order of the tracks
    sorted_playlist['new_order'] = sorted_playlist.index + 1

    # Save sorted playlist
    output_file = os.path.join('../data', 'playlist_sorted.csv')
    sorted_playlist.to_csv(output_file, index=False)

    print("Playlist sorted and saved to 'playlist_sorted.csv'")

if __name__ == "__main__":
    main()