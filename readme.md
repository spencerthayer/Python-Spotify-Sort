# Spotify Playlist Swarm Sorting

### Overview

**Python Spotify Sort** is a tool designed to enhance the listening experience by intelligently sorting Spotify playlists. Utilizing the Particle Swarm Optimization (PSO) algorithm, it attempts to create a smooth transition between tracks based on their musical features. PSO is an optimization algorithm that tries to understand the social behavior of travelling ants, flocking birds, schooling fish, or any swarm of particles that moves through a solution space to find an optimal organic ordering.

### Methodology

#### 1. **Feature Extraction**:
   The application starts by extracting audio features of the tracks using Spotify's Web API. These features include tempo, danceability, energy, and others that characterize the music.

#### 2. **Fitness Function Definition**:
   A fitness function is defined to evaluate how well a given sequence of songs matches the desired flow of the playlist. This function takes into account the differences in musical features between consecutive tracks.

#### 3. **Particle Swarm Optimization Algorithm**:
   PSO simulates a flock of birds searching for the best location. In our case, each "bird" or particle represents a potential playlist order. Particles explore the solution space and adjust their positions based on their own experience and that of their neighbors to find the most harmonious playlist sequence.

   Unlike the nearest neighbor algorithm, PSO considers the global best solution found by any particle, which helps in avoiding local minima and tends towards a more globally optimal playlist order.

#### 4. **Playlist Rearrangement**:
   Once the optimal sequence is determined, the playlist is rearranged accordingly. This leads to a playlist where the transition between individual songs is smooth but not uniform and predicatble thus enhancing the wholistic listening experience of the playlist in a more organic manner.


### Conclusion

**Python Spotify Sort** leverages the robustness of PSO to solve the complex task of playlist sorting. By treating the sequence of songs as a multidimensional space, PSO navigates through various possibilities to find a sequence that provides a cohesive listening experience. The final playlist is a result of a sophisticated computational process, mirroring the natural behavior of swarms.


### Requirements
This program uses the spotipy & python_tsp libraries.

`pip install -r requirements.txt`

You also need a spotify api key, you can get one [here](https://developer.spotify.com/dashboard/).