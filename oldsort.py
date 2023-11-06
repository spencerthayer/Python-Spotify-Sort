import numpy as np
from python_tsp.heuristics import solve_tsp_simulated_annealing
import csv
from random import shuffle
from tqdm import tqdm
import time
import signal

def solve_tsp_simulated_annealing_debug(*args, **kwargs):
    print("Starting TSP solving...")
    start_time = time.time()
    
    try:
        result = solve_tsp_simulated_annealing(*args, **kwargs)
    except Exception as e:
        print("An error occurred:", str(e))
        return None
    
    end_time = time.time()
    print("TSP solving completed in", end_time - start_time, "seconds")
    return result

filename = "spotify_features.csv"

def try_type(value):
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value

# Read and shuffle tracks
with open(filename, "r") as csvfile:
    reader = csv.reader(csvfile)
    header, *tracks = list(reader)
    tracks = [dict(zip(map(str.strip, header), map(try_type, track))) for track in tracks]

min_tempo, max_tempo = min(track["tempo"] for track in tracks), max(track["tempo"] for track in tracks)

def distance_function(track1, track2):
    same_mode = track1["mode"] == track2["mode"]
    key1 = track1["key"]
    key2 = track2["key"]
    if same_mode:
        key_diff = min(abs(key1 - key2), 12 - abs(key1 - key2))
        key_distance = 0.5 if key_diff == 6 else min(key_diff, 2) / 4
    else:
        key_distance = 0 if key1 == key2 else 1

    tempo1 = (track1["tempo"] - min_tempo) / (max_tempo - min_tempo)
    tempo2 = (track2["tempo"] - min_tempo) / (max_tempo - min_tempo)
    tempo_distance = abs(tempo1 - tempo2)

    loudness1 = (track1["loudness"] + 60) / 60
    loudness2 = (track2["loudness"] + 60) / 60
    loudness_distance = abs(loudness1 - loudness2)

    energy_distance = abs(track1["energy"] - track2["energy"])
    valence_distance = abs(track1["valence"] - track2["valence"])
    danceability_distance = abs(track1["danceability"] - track2["danceability"])

    weights = {
        "key_weight": 3,
        "tempo_weight": 0,
        "loudness_weight": 0,
        "energy_weight": 3,
        "valence_weight": 4,
        "danceability_weight": 2,
    }

    song_distance = sum([
        key_distance * weights["key_weight"],
        tempo_distance * weights["tempo_weight"],
        loudness_distance * weights["loudness_weight"],
        energy_distance * weights["energy_weight"],
        valence_distance * weights["valence_weight"],
        danceability_distance * weights["danceability_weight"],
    ])

    return song_distance

# Calculate distance matrix
print("Calculating distance matrix...")
distances = np.array([[distance_function(track1, track2) for track2 in tracks] for track1 in tracks])
distances[:, 0] = 0
x0 = list(range(len(tracks)))
shuffle(x0)

print("Starting TSP solving...")

####### START TIME OUT 
# Wrap the TSP solving with tqdm for a progress bar
start_time = time.time()
progress_bar = tqdm(range(1000), desc="Solving TSP")

def handler(signum, frame):
    global counter
    counter -= 1
    if counter <= 0:
        raise TimeoutError("TSP solving took too long")
    else:
        progress_bar.set_description(f"Solving TSP - Time remaining: {counter}s")
        signal.alarm(1)  # Set the alarm to trigger every second

# Set the signal handler
signal.signal(signal.SIGALRM, handler)

for iteration in progress_bar:
    print("Iteration:", iteration)
    
    # Print parameters
    print("Distances Matrix Shape:", distances.shape)
    print("Initial Solution (x0):", x0)
    print("Alpha:", 0.999)
    
    try:
        # Set an alarm for 300 seconds (5 minutes)
        global counter
        counter = 300  # Set the counter to 300 seconds
        signal.alarm(1)  # Trigger the alarm every second

        # Monitor execution time and use the debug function
        start_tsp = time.time()
        result = solve_tsp_simulated_annealing_debug(distances, x0=x0, alpha=0.999)
        end_tsp = time.time()

        # Cancel the alarm
        signal.alarm(0)

        # Unpack and print the results only if the result is not None
        if result is not None:
            permutation, distance = result
            print("TSP solving time for iteration", iteration, ":", end_tsp - start_tsp, "seconds")
            print("Permutation:", permutation)
            print("Distance:", distance)
    except TimeoutError as e:
        print(str(e))
        break

    time.sleep(0.01)  # simulate some time delay for each iteration, remove in actual code
end_time = time.time()
####### END TIME OUT

print("TSP solved, writing to CSV...")

print(f"Time taken: {end_time - start_time:.2f} seconds")

# Save sorted tracks to CSV
with open("sorted_tracks.csv", "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow([
        "track",
        "uri",
        "old_order",
        "new_order",
        "key",
        "mode",
        "energy",
        "valence",
        "danceability",
        "tempo",
        "loudness",
    ])
    for new_pos, i in enumerate(permutation):
        track = tracks[i]
        writer.writerow([
            track["name"],
            track["uri"],
            tracks.index(tracks[i]) + 1,
            new_pos + 1,
            track["key"],
            track["mode"],
            track["energy"],
            track["valence"],
            track["danceability"],
            track["tempo"],
            track["loudness"],
        ])

# Print track transitions
for i, j in zip(permutation, permutation[1:]):
    print(f"{tracks[i]['name']} --> {tracks[j]['name']}")

# Print normalized distance
weights = {
    "key_weight": 3,
    "tempo_weight": 0,
    "loudness_weight": 0,
    "energy_weight": 3,
    "valence_weight": 4,
    "danceability_weight": 2,
}
normalized_distance = distance / sum(weights.values())
avg_distance_per_track = normalized_distance / len(tracks)

print(f"Normalized distance: {normalized_distance}\nAverage distance per track: {avg_distance_per_track}")

print("Process completed successfully! Your playlist has been sorted.")
