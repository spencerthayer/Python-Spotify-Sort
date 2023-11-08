import os
import csv
from spotify_client import get_spotify_client, get_playlist_items
from time import sleep
import json

# Ensure the directory exists
os.makedirs(os.path.dirname('../data/'), exist_ok=True)

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the path to the data directory
data_dir = os.path.join(script_dir, '..', 'data')

sp = get_spotify_client()

# The path to the 'playlists.json' file
playlists_json_path = os.path.join(data_dir, 'playlists.json')

# Load the playlist ID from the JSON file
with open(playlists_json_path, 'r') as file:
    playlists_data = json.load(file)
    playlist = playlists_data['ID']  # Extract the playlist ID using the new "ID" key

results = get_playlist_items(sp, playlist)

# open playlist_sorted.csv and read into a list, sort on new_order
with open(os.path.join(data_dir, "playlist_sorted.csv"), "r") as csvfile:
    reader = csv.reader(csvfile)
    # read tracks zip with header
    header, *rows = reader
    tracks = [dict(zip(header, row)) for row in rows]

    # update old_order with old_order from results["items"]
    old_orders = [i["track"]["uri"] for i in results["items"]]
    for track in tracks:
        # print(track["uri"])
        if track["uri"] in old_orders:
            track["old_order"] = old_orders.index(track["uri"])
        else:
            # handle the case when track["uri"] is not in old_orders
            pass

    tracks = sorted(tracks, key=lambda x: int(x["old_order"]))

new_orders = [int(track["new_order"]) - 1 for track in tracks]

# use new orders to reorder items into the right order
for i in range(len(new_orders)):
    track_to_be_moved = new_orders.index(i)
    if i == track_to_be_moved:
        continue
    sp.playlist_reorder_items(playlist, track_to_be_moved, i)
    new_orders.insert(i, new_orders.pop(track_to_be_moved))
    sleep(0.5)  # be a good internet citizen

print("Process completed successfully! Spotify playlist has been updated.")