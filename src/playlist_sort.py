import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from sklearn.preprocessing import MinMaxScaler
import os

# Ensure the directory exists
os.makedirs(os.path.dirname('../data/'), exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the data directory
data_dir = os.path.join(script_dir, '..', 'data')

# PSO Helper Functions
def calculate_key_compatibility(key1, key2):
    # Assuming keys are numerical, compatibility could be improved beyond binary
    # For simplicity, we'll keep binary compatibility: 1 for match, 0 otherwise
    return 1 if key1 == key2 else 0

def calculate_fitness(order, features_df):
    # Exclude non-numeric columns from scaling
    non_numeric_columns = features_df.select_dtypes(exclude=['int64', 'float64']).columns
    numeric_features = features_df.drop(columns=non_numeric_columns)
    
    # Scale only the numeric features
    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(numeric_features)
    
    # Create a DataFrame with scaled values for distance calculation
    scaled_df = pd.DataFrame(scaled_features, columns=numeric_features.columns, index=features_df.index)
    
    # Calculate euclidean distances using the scaled numeric features
    distance_matrix = euclidean_distances(scaled_df.loc[order], scaled_df.loc[order])
    
    # Compute the sum of distances for the given order
    total_distance = sum(distance_matrix[i, i+1] for i in range(len(order)-1))
    
    # Calculate key compatibility and tempo smoothness if 'key' and 'tempo' are numeric
    # If 'key' and 'tempo' are not numeric, appropriate conversion or handling is needed
    if 'key' in numeric_features.columns and 'tempo' in numeric_features.columns:
        key_compatibility = sum(features_df.iloc[order[i]]['key'] == features_df.iloc[order[i+1]]['key']
                                for i in range(len(order)-1))
        tempo_smoothness = sum(abs(features_df.iloc[order[i]]['tempo'] - features_df.iloc[order[i+1]]['tempo'])
                               for i in range(len(order)-1))
    else:
        # Handle non-numeric 'key' and 'tempo' appropriately
        key_compatibility = 0
        tempo_smoothness = 0
    
    # Fitness calculation
    return key_compatibility - tempo_smoothness - total_distance

# Placeholder function to apply discrete velocity to particles
def apply_discrete_velocity(particle, discrete_velocity):
    # Implement the logic to update particle index based on discrete_velocity
    # This should be a permutation of the tracks indices
    # For example, if the velocity suggests swapping two tracks, implement this swap
    return particle # This line is a placeholder and should be replaced with actual implementation

# PSO Algorithm
def particle_swarm_optimization(features_df, num_particles=30, iterations=100):
    num_tracks = len(features_df)
    
    # Initialize particles
    particles = [np.random.permutation(num_tracks) for _ in range(num_particles)]
    velocities = [np.zeros(num_tracks) for _ in range(num_particles)]
    personal_best_positions = list(particles)
    personal_best_scores = [calculate_fitness(p, features_df) for p in particles]
    global_best_position = particles[np.argmax(personal_best_scores)]
    global_best_score = max(personal_best_scores)
    
    for _ in range(iterations):
        for i in range(num_particles):
            # Update velocities
            inertia = 0.5  # Inertia weight to control the impact of the previous velocity
            cognitive_component = 0.5  # Cognitive weight to control the impact of the particle's own experience
            social_component = 0.5  # Social weight to control the impact of the swarm's experience
            random_factors = (np.random.rand(2) - 0.5) * 2  # Random factors for cognitive and social components
            
            # Update velocities
            velocities[i] = (inertia * velocities[i] +
                             cognitive_component * random_factors[0] * (personal_best_positions[i] - particles[i]) +
                             social_component * random_factors[1] * (global_best_position - particles[i]))
            
            # Discretize the change in position to apply to particle's index permutation
            discrete_velocity = np.round(velocities[i]).astype(int)
            
            # Update particles using discrete velocity
            particles[i] = apply_discrete_velocity(particles[i], discrete_velocity)
            
            # Update personal bests
            current_fitness = calculate_fitness(particles[i], features_df)
            if current_fitness > personal_best_scores[i]:
                personal_best_scores[i] = current_fitness
                personal_best_positions[i] = particles[i]
                
            # Update global best
            if current_fitness > global_best_score:
                global_best_score = current_fitness
                global_best_position = particles[i]
    
    return global_best_position

def main():
    # Load the playlist features from the CSV file
    input_file = os.path.join(data_dir, 'playlist_features.csv')
    features_df = pd.read_csv(input_file)
    
    # Ensure 'key' is treated as numeric
    features_df['key'] = pd.to_numeric(features_df['key'], errors='coerce')
    
    # Run the PSO algorithm
    best_order = particle_swarm_optimization(features_df)
    
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
