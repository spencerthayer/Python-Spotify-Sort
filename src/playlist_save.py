import csv
from spotify_client import get_spotify_client, get_playlist_items
import os

# Ensure the directory exists
os.makedirs(os.path.dirname('../data/'), exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the data directory
data_dir = os.path.join(script_dir, '..', 'data')

sp = get_spotify_client()

playlist = os.getenv("PLAYLIST")

# get length of playlist
playlist_len = sp.playlist(playlist_id=playlist)["tracks"]["total"]

# read result in chunks of 100
results = get_playlist_items(sp, playlist)

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
# with open("../data/playlist_features.csv", "w", newline='') as csvfile:
with open(os.path.join(data_dir, 'playlist_features.csv'), 'w', newline='') as csvfile:
    fieldnames = [
        "idx",
        "name",
        "uri",
        "key",
        "mode",
        "danceability",
        "energy",
        "loudness",
        "acousticness",
        "instrumentalness",
        "liveness",
        "valence",
        "tempo",
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for idx, item in enumerate(results["items"], 1):
        track = item["track"]
        feature = features[idx - 1]
        writer.writerow(
            {
                "idx": idx,
                "name": track["name"],
                "uri": track["uri"],
                "key": feature["key"],
                "mode": feature["mode"],
                "danceability": feature["danceability"],
                "energy": feature["energy"],
                "loudness": feature["loudness"],
                "acousticness": feature["acousticness"],
                "instrumentalness": feature["instrumentalness"],
                "liveness": feature["liveness"],
                "valence": feature["valence"],
                "tempo": feature["tempo"],
            }
        )

print("Process completed successfully! Playlist features have been saved.")