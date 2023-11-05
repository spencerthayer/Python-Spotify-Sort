# Python Spotify Sort
Playlist Optimization using Nearest Neighbor to Solve for the Traveling Salesperson Problem

### Overview

**Python Spotify Sort** is an innovative solution designed to optimize the listening experience of a Spotify playlist by rearranging the songs in a manner that ensures a smooth and cohesive transition between consecutive tracks. Drawing inspiration from the Traveling Salesperson Problem (TSP), this script leverages the nearest neighbor algorithm to find an approximate solution to the ordering dilemma.

The Traveling Salesperson Problem is a classic optimization problem, where given a list of cities and the distances between each pair of cities, the task is to find the shortest possible route that visits each city exactly once and returns to the original city. In the context of playlist optimization, each song can be thought of as a city, and the "distance" between songs is determined by the dissimilarity in their features, such as tempo, key, valence, and energy.

### Methodology

#### 1. **Feature Extraction**:
   The script begins by extracting relevant features of the tracks in the playlist using Spotify's Web API. These features encapsulate various musical aspects of the tracks, such as tempo, danceability, energy, loudness, valence, etc.

#### 2. **Distance Computation**:
   The "distance" or dissimilarity between two songs is computed by calculating the Euclidean distance between their feature vectors. This step essentially translates the playlist optimization problem into a TSP, where the cities are songs and distances represent how dissimilar two songs are.

#### 3. **Nearest Neighbor Algorithm**:
   To solve this transformed TSP, the script employs the nearest neighbor algorithm. This heuristic algorithm starts at an arbitrary song and repeatedly visits the nearest unvisited song until all songs are visited. The approach is based on the principle of locality and is known to provide a good approximation to the optimal solution in a relatively short time.

   The nearest neighbor algorithm is particularly suitable for large playlists as it is computationally less intensive compared to exact algorithms for TSP, while still yielding satisfactory results.

#### 4. **Playlist Rearrangement**:
   The script then rearranges the playlist based on the order determined by the nearest neighbor algorithm. This ensures that songs with similar features are placed next to each other, creating a seamless and enjoyable listening experience.

### Conclusion

Python Spotify Sort offers an intelligent and efficient approach to playlist optimization. By interpreting the problem through the lens of the Traveling Salesperson Problem and applying the nearest neighbor algorithm, it crafts a playlist where each track naturally flows into the next. The result is a harmonious and engaging auditory journey that enhances the listener's experience.


### Requirements
This program uses the spotipy & python_tsp libraries.

`pip install -r requirements.txt`

You also need a spotify api key, you can get one [here](https://developer.spotify.com/dashboard/).