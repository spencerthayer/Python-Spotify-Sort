import os
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

def get_spotify_client(scope="playlist-modify-public playlist-modify-private user-library-read"):
    return Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_playlist_length(sp, playlist_id):
    return sp.playlist(playlist_id=playlist_id)["tracks"]["total"]

def get_playlist_items(sp, playlist_id, limit=100):
    results = {"items": []}
    playlist_len = get_playlist_length(sp, playlist_id)
    for i in range(0, playlist_len, limit):
        new_results = sp.playlist_items(fields=["items"], playlist_id=playlist_id, limit=limit, offset=i)
        results["items"].extend(new_results["items"])
    return results
