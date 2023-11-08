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

# Define a regular expression pattern for Spotify playlist IDs
# Spotify IDs are typically 22 alphanumeric characters
playlist_id_pattern = re.compile(r'^[A-Za-z0-9]{22}$')

# Remove all keys that match the Spotify playlist ID pattern
playlist_weights = {k: v for k, v in weights.items() if not playlist_id_pattern.match(k)}

# Debugging print statements
print('Debugging: Loaded weights from JSON:', playlist_weights)
print('Debugging: Path to playlists.json:', os.path.join(data_dir, 'playlists.json'))

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

# def particle_swarm_optimization(features_df, weightings, **pso_params):
    # num_particles = pso_params['num_particles']
    # iterations = pso_params['iterations']
    # # Number of features (tracks)
    # num_features = features_df.shape[0]

    # # Initialize particle positions to random permutations of the indices representing songs
    # particle_positions = [np.random.permutation(num_features) for _ in range(num_particles)]
    # particle_velocities = [np.zeros(num_features) for _ in range(num_particles)]
    # particle_best_positions = list(particle_positions)  # Each particle's best position is its starting position
    # particle_best_fitness = [calculate_fitness(p, features_df, weightings) for p in particle_best_positions]
    # global_best_position = particle_best_positions[np.argmin(particle_best_fitness)]
    # global_best_fitness = min(particle_best_fitness)

    # # Constants for the PSO algorithm
    # w = 0.5  # Inertia weight
    # c1 = 0.8  # Cognitive/personal best weight
    # c2 = 0.9  # Social/global best weight

    # # Function to update the velocity and position of the particles
    # def update_particles(particle_positions, particle_velocities, particle_best_positions, global_best_position):
    #     for i in range(num_particles):
    #         # Update velocity
    #         r1, r2 = np.random.rand(2)  # random coefficients
    #         particle_velocities[i] = (
    #             w * particle_velocities[i]
    #             + c1 * r1 * (particle_best_positions[i] - particle_positions[i])
    #             + c2 * r2 * (global_best_position - particle_positions[i])
    #         )

    #         # Update position with new velocity
    #         particle_positions[i] += particle_velocities[i].astype(int)

    #         # Ensure the particle positions are permutations (handle potential duplicates and missing values)
    #         particle_positions[i] = np.array(list(range(num_features)))[np.argsort(np.argsort(particle_positions[i]))]

    # # Main loop of PSO
    # for iteration in range(iterations):
    #     for i in range(num_particles):
    #         # Calculate fitness for particles
    #         current_fitness = calculate_fitness(particle_positions[i], features_df, weightings)

    #         # Update personal best
    #         if current_fitness < particle_best_fitness[i]:
    #             particle_best_fitness[i] = current_fitness
    #             particle_best_positions[i] = particle_positions[i]

    #         # Update global best
    #         if current_fitness < global_best_fitness:
    #             global_best_fitness = current_fitness
    #             global_best_position = particle_positions[i]

    #     # Update particles
    #     update_particles(particle_positions, particle_velocities, particle_best_positions, global_best_position)

    # return global_best_position
# # # # # #
def particle_swarm_optimization(features_df, weightings, **pso_params):
    num_particles = pso_params['num_particles']
    iterations = pso_params['iterations']
    # Number of features (tracks)
    num_features = features_df.shape[0]

    # Initialize particle positions to random permutations of the indices representing songs
    particle_positions = [np.random.permutation(num_features) for _ in range(num_particles)]
    particle_velocities = [np.zeros(num_features) for _ in range(num_particles)]
    particle_best_positions = list(particle_positions)  # Each particle's best position is its starting position
    particle_best_fitness = [calculate_fitness(p, features_df, weightings) for p in particle_best_positions]
    global_best_position = particle_best_positions[np.argmin(particle_best_fitness)]
    global_best_fitness = min(particle_best_fitness)

    # Adaptive inertia weight (start high for exploration and end low for exploitation)
    w_start = 0.9
    w_end = 0.4
    w = w_start

    # Slightly tuned cognitive/personal best weight and social/global best weight
    c1 = 0.5  # Cognitive/personal best weight
    c2 = 0.6  # Social/global best weight

    # Function to update the velocity and position of the particles
    def update_particles(particle_positions, particle_velocities, particle_best_positions, global_best_position, w):
        for i in range(num_particles):
            # Update velocity
            r1, r2 = np.random.rand(2)  # random coefficients
            particle_velocities[i] = (
                w * particle_velocities[i]
                + c1 * r1 * (particle_best_positions[i] - particle_positions[i])
                + c2 * r2 * (global_best_position - particle_positions[i])
            )

            # Update position with new velocity
            particle_positions[i] += particle_velocities[i].astype(int)

            # Ensure the particle positions are permutations (handle potential duplicates and missing values)
            particle_positions[i] = np.array(list(range(num_features)))[np.argsort(np.argsort(particle_positions[i]))]

    # Main loop of PSO
    for iteration in range(iterations):
        # Update inertia weight
        w = w_start - ((w_start - w_end) * (iteration / iterations))

        for i in range(num_particles):
            # Calculate fitness for particles
            current_fitness = calculate_fitness(particle_positions[i], features_df, weightings)

            # Update personal best
            if current_fitness < particle_best_fitness[i]:
                particle_best_fitness[i] = current_fitness
                particle_best_positions[i] = particle_positions[i]

            # Update global best
            if current_fitness < global_best_fitness:
                global_best_fitness = current_fitness
                global_best_position = particle_positions[i]

        # Update particles
        update_particles(particle_positions, particle_velocities, particle_best_positions, global_best_position, w)

    return global_best_position

# The rest of the code remains the same up until the main function
def main():
    # Load the playlist features from the CSV file
    input_file = os.path.join(data_dir, 'playlist_features.csv')
    features_df = pd.read_csv(input_file)

    # Ensure 'key' is treated as numeric
    features_df['key'] = pd.to_numeric(features_df['key'], errors='coerce')

    # Run the PSO algorithm with the weighted features
    best_order = particle_swarm_optimization(features_df, playlist_weights, num_particles=num_particles, iterations=iterations)

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
