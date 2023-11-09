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

# Define the fitness function
def calculate_fitness(particle, features_df, weightings):
    # Calculate the fitness of the particle based on the weighted features
    fitness = 0
    for i in range(len(particle) - 1):
        for feature, weight in weightings.items():
            # Ensure the feature exists in the dataframe to avoid KeyError
            if feature in features_df.columns:
                fitness += weight * (features_df.at[particle[i], feature] - features_df.at[particle[i+1], feature]) ** 2
    return -fitness  # Negative because we want to minimize the distance

# # # T H E # M A G I C# # #
def particle_swarm_optimization(features_df, weightings, **pso_params):
    # Extracting parameters for the PSO algorithm
    num_particles = pso_params['num_particles']  # Number of particles in the swarm
    iterations = pso_params['iterations']        # Number of iterations for the algorithm

    # Number of features (tracks) in the dataset
    num_features = features_df.shape[0]

    # Initialize particle positions
    if randomize:
        # If randomize is True, start each particle at a random permutation of the indices (song indices)
        particle_positions = [np.random.permutation(num_features) for _ in range(num_particles)]
    else:
        # If randomize is False, start all particles at the same position, based on sorted feature weights
        sorted_indices = np.argsort([np.sum(features_df[col] * weightings.get(col, 0)) for col in features_df.columns])
        # Adjust length of initial position to match num_features
        if len(sorted_indices) < num_features:
            # Append missing indices if sorted_indices are fewer than num_features
            missing_indices = np.setdiff1d(np.arange(num_features), sorted_indices)
            initial_position = np.concatenate([sorted_indices, missing_indices])
        elif len(sorted_indices) > num_features:
            # Truncate sorted_indices if they are more than num_features
            initial_position = sorted_indices[:num_features]
        else:
            initial_position = sorted_indices
        particle_positions = [initial_position for _ in range(num_particles)]

    # Initialize particle velocities as zero arrays
    particle_velocities = [np.zeros(num_features) for _ in range(num_particles)]

    # Initialize each particle's best position as its starting position
    particle_best_positions = list(particle_positions)

    # Calculate the initial best fitness values for each particle
    particle_best_fitness = [calculate_fitness(p, features_df, weightings) for p in particle_best_positions]

    # Determine the global best particle position and its fitness
    global_best_position = particle_best_positions[np.argmin(particle_best_fitness)]
    global_best_fitness = min(particle_best_fitness)

    # Initialize adaptive inertia weight parameters
    w_start = 0.9  # Initial inertia weight
    w_end = 0.4    # Final inertia weight
    w = w_start    # Current inertia weight

    # Cognitive and social coefficients
    c1 = 0.5  # Cognitive/personal best weight
    c2 = 0.6  # Social/global best weight

    # Function to update the velocity and position of particles
    def update_particles(particle_positions, particle_velocities, particle_best_positions, global_best_position, w):
        for i in range(num_particles):
            # Generate random coefficients for velocity update
            r1, r2 = np.random.rand(2)

            # Update particle velocity
            particle_velocities[i] = (
                w * particle_velocities[i] +
                c1 * r1 * (particle_best_positions[i] - particle_positions[i]) +
                c2 * r2 * (global_best_position - particle_positions[i])
            )

            # Update particle position with new velocity
            particle_positions[i] += particle_velocities[i].astype(int)

            # Correct particle position to ensure it remains a permutation of song indices
            particle_positions[i] = np.array(list(range(num_features)))[np.argsort(np.argsort(particle_positions[i]))]

    # Main loop of the PSO algorithm
    for iteration in range(iterations):
        # Update inertia weight linearly between w_start and w_end
        w = w_start - ((w_start - w_end) * (iteration / iterations))

        # Iterate over each particle
        for i in range(num_particles):
            # Calculate current fitness for the particle
            current_fitness = calculate_fitness(particle_positions[i], features_df, weightings)

            # Update personal best if current fitness is better
            if current_fitness < particle_best_fitness[i]:
                particle_best_fitness[i] = current_fitness
                particle_best_positions[i] = particle_positions[i]

            # Update global best if current fitness is the best overall
            if current_fitness < global_best_fitness:
                global_best_fitness = current_fitness
                global_best_position = particle_positions[i]

        # Update particle velocities and positions
        update_particles(particle_positions, particle_velocities, particle_best_positions, global_best_position, w)

    # Return the best particle position (global best) at the end of iterations
    return global_best_position
# # # # # #

# The rest of the code remains the same up until the main function
def main():
    # Load the playlist features from the CSV file
    input_file = os.path.join(data_dir, 'playlist_features.csv')
    features_df = pd.read_csv(input_file)

    # Ensure 'key' is treated as numeric
    features_df['key'] = pd.to_numeric(features_df['key'], errors='coerce')

    # Run the PSO algorithm with the weighted features
    best_order = particle_swarm_optimization(features_df, playlist_weights, randomize=randomize, num_particles=num_particles, iterations=iterations)

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
