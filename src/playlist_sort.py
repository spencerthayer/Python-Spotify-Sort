import json
import pandas as pd
import numpy as np
import os
import re

# Ensure the directory exists
os.makedirs(os.path.dirname('../data/'), exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the data directory
data_dir = os.path.join(script_dir, '..', 'data')

# Read the weights from the JSON file
with open(os.path.join(data_dir, 'playlists.json'), 'r') as json_file:
    weights = json.load(json_file)
    
# Extract the randomize value
randomize = weights.pop('randomize', True)  # Default to True if not found

# Define a regular expression pattern for Spotify playlist IDs
# Spotify IDs are typically 22 alphanumeric characters
playlist_id_pattern = re.compile(r'^[A-Za-z0-9]{22}$')

# Remove all keys that match the Spotify playlist ID pattern
playlist_weights = {k: v for k, v in weights.items() if not playlist_id_pattern.match(k)}

# Debugging print statements
print('Debugging: Loaded weights from JSON:', playlist_weights)
# print('Debugging: Path to playlists.json:', os.path.join(data_dir, 'playlists.json'))

# Adjust the PSO parameters based on weights
num_particles = int(playlist_weights.pop('num_particles'))
iterations = int(playlist_weights.pop('iterations'))

# Circle of Fifths Compatibility Check Function
def is_compatible_circle_of_fifths(key1, mode1, key2, mode2):
    # Major keys are 0 steps away on the circle from themselves, minor keys are 3 steps away.
    major_keys = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]  # C, G, D, A, E, B, F♯, C♯, A♭, E♭, B♭, F
    minor_keys = [(k + 3) % 12 for k in major_keys]      # A, E, B, F♯, C♯, G♯, D♯, A♯, F, C, G, D

    key1_circle = major_keys[key1] if mode1 == 1 else minor_keys[key1]
    key2_circle = major_keys[key2] if mode2 == 1 else minor_keys[key2]

    # Check if keys are the same or adjacent in the Circle of Fifths
    return key1_circle == key2_circle or abs(key1_circle - key2_circle) == 1
    print(f"Distance: {key1_circle}")

# Function to calculate the distance between two keys in the Circle of Fifths
def circle_of_fifths_distance(key1, mode1, key2, mode2):
    major_keys = [0, 7, 2, 9, 4, 11, 6, 1, 8, 3, 10, 5]
    minor_keys = [(k + 3) % 12 for k in major_keys]

    key1_circle = major_keys[key1] if mode1 == 1 else minor_keys[key1]
    key2_circle = major_keys[key2] if mode2 == 1 else minor_keys[key2]

    # Calculate the minimum circular distance
    distance = min(abs(key1_circle - key2_circle), 12 - abs(key1_circle - key2_circle))
    return distance
    print(f"Distance: {distance}")

def calculate_fitness(particle, features_df, weightings):
    # Initialize fitness
    fitness = 0

    # Iterate over each track in the particle's ordering
    for i in range(len(particle) - 1):
        current_track = features_df.iloc[particle[i]]
        next_track = features_df.iloc[particle[i + 1]]

        # Calculate the weighted difference for each feature
        for feature, weight in weightings.items():
            if feature in features_df.columns:
                difference = abs(current_track[feature] - next_track[feature])
                fitness += weight * difference

    return -fitness  # Negative because we want to minimize the fitness
    print(f"Fitness: -{fitness}")

# # # # # Particle Swarm Optimization Algorithm
def particle_swarm_optimization(features_df, weightings, num_particles, iterations):
    num_tracks = features_df.shape[0]  # Number of tracks

    # Initialize particle positions with random permutations of track indices
    particle_positions = [np.random.permutation(num_tracks) for _ in range(num_particles)]

    # Initialize particle velocities
    particle_velocities = [np.zeros(num_tracks) for _ in range(num_particles)]

    # Initialize best positions and fitness of particles
    particle_best_positions = list(particle_positions)
    particle_best_fitness = [calculate_fitness(p, features_df, weightings) for p in particle_best_positions]

    # Determine global best
    global_best_index = np.argmin(particle_best_fitness)
    global_best_position = particle_best_positions[global_best_index]
    global_best_fitness = particle_best_fitness[global_best_index]

    # PSO parameters for inertia, cognitive, and social components
    w_start, w_end = 0.9, 0.4  # Inertia weight start and end
    c1, c2 = 2.0, 2.0  # Cognitive and social components

    # Main loop of PSO
    for iteration in range(iterations):
        # Linearly decreasing inertia weight
        w = w_start - ((w_start - w_end) * iteration / iterations)

        for i in range(num_particles):
            r1, r2 = np.random.rand(2)  # Random coefficients

            # Update velocities
            particle_velocities[i] = (w * particle_velocities[i] +
                                      c1 * r1 * (particle_best_positions[i] - particle_positions[i]) +
                                      c2 * r2 * (global_best_position - particle_positions[i]))

            # Apply the velocity changes and maintain the indices within the range
            particle_positions[i] = (particle_positions[i] + particle_velocities[i].astype(int)) % num_tracks
            particle_positions[i] = np.argsort(particle_positions[i])  # Keep the order within the track index range

            # Evaluate current fitness
            current_fitness = calculate_fitness(particle_positions[i], features_df, weightings)

            # Update best position and fitness for each particle
            if current_fitness < particle_best_fitness[i]:
                particle_best_positions[i] = particle_positions[i]
                particle_best_fitness[i] = current_fitness

            # Update global best
            if current_fitness < global_best_fitness:
                global_best_position = particle_positions[i]
                global_best_fitness = current_fitness

    return global_best_position
# # # # # End of Particle Swarm Optimization Algorithm

# The main function is where we integrate everything together. It will load the data, run the Particle Swarm Optimization (PSO) algorithm, and then output the sorted playlist.
def main():
    # Load the playlist features from the CSV file
    input_file = os.path.join(data_dir, 'playlist_features.csv')
    features_df = pd.read_csv(input_file)

    # Ensure 'key' is treated as numeric
    features_df['key'] = pd.to_numeric(features_df['key'], errors='coerce')

    # Define the PSO parameters
    num_particles = int(playlist_weights.pop('num_particles', 50))  # Default to 50 if not found
    iterations = int(playlist_weights.pop('iterations', 2000))     # Default to 2000 if not found

    # Run the PSO algorithm with the weighted features
    best_order = particle_swarm_optimization(features_df, playlist_weights, num_particles, iterations)

    # Apply the sorted order to the DataFrame
    sorted_playlist = features_df.iloc[best_order].reset_index(drop=True)

    # Create 'new_order' column corresponding to the sorted order
    sorted_playlist['new_order'] = range(1, len(sorted_playlist) + 1)

    # Save the sorted playlist to a new CSV file
    output_file = os.path.join(data_dir, 'playlist_sorted.csv')
    sorted_playlist.to_csv(output_file, index=False)

    print(f'Playlist sorted and saved to {output_file}')

if __name__ == '__main__':
    main()
