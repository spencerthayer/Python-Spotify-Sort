import csv
from spotify_client import get_spotify_client, get_playlist_items
import os
import json

# Ensure the directory exists
os.makedirs(os.path.dirname('../data/'), exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the 'data' directory
data_dir = os.path.join(script_dir, '..', 'data')

# The path to the 'playlists.json' file
playlists_json_path = os.path.join(data_dir, 'playlists.json')

# Load the playlist ID from the JSON file
with open(playlists_json_path, 'r') as file:
    playlists_data = json.load(file)
    playlist_id = playlists_data['id']  # Extract the playlist ID using the new "ID" key

# The rest of your code follows, properly indented
sp = get_spotify_client()

# Use the extracted playlist ID
playlist_len = sp.playlist(playlist_id=playlist_id)["tracks"]["total"]

# read result in chunks of 100
results = get_playlist_items(sp, playlist_id)

for idx, item in enumerate(results["items"], 1):
    track = item["track"]
    print(idx, track["artists"][0]["name"], " – ", track["name"])

# get all track uri's from results
track_uris = [item["track"]["uri"] for item in results["items"]]
features = []
# get features for each track in chunks of 100
for i in range(0, len(track_uris), 100):
    features.extend(sp.audio_features(track_uris[i:i+100]))

# save track features to csv
with open(os.path.join(data_dir, 'playlist_features.csv'), 'w', newline='') as csvfile:
    # Define the basic fieldnames, keeping 'idx' and 'name' at the front
    # and sorting the rest alphabetically
    fieldnames = [
        "idx",
        "name",
        "artist",
        "acousticness",
        "danceability",
        "duration_ms",
        "energy",
        "instrumentalness",
        "key",
        "liveness",
        "loudness",
        "mode",
        "speechiness",
        "tempo",
        "time_signature",
        "uri",
        "valence"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for idx, item in enumerate(results["items"], 1):
        track = item["track"]
        feature = features[idx - 1]
        artist_name = track["artists"][0]["name"] if track["artists"] else ""
        writer.writerow(
            {
                "idx": idx,
                "name": track["name"],
                "artist": artist_name,
                "acousticness": feature["acousticness"],
                "danceability": feature["danceability"],
                "duration_ms": feature["duration_ms"],
                "energy": feature["energy"],
                "instrumentalness": feature["instrumentalness"],
                "key": feature["key"],
                "liveness": feature["liveness"],
                "loudness": feature["loudness"],
                "mode": feature["mode"],
                "speechiness": feature["speechiness"],
                "tempo": feature["tempo"],
                "time_signature": feature["time_signature"],
                "uri": track["uri"],
                "valence": feature["valence"]
            }
        )

print("Process completed successfully! Playlist features have been saved.")
