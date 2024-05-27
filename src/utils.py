# Utilities

# Initialise
import requests
import base64
import json
import os
import spotipy as sp
import pandas as pd
import spotipy.util as util
import pandas as pd
from spotipy.oauth2 import SpotifyClientCredentials
import time

# Function to retrieve musical features of tracks
def get_audio_features(token, track_ids, retries=3, delay=500):
    '''
    Retrieve audio features for a list of track IDs, with retry logic for handling temporary server errors.
    '''
    headers = {"Authorization": f"Bearer {token}"}
    features_url = "https://api.spotify.com/v1/audio-features"
    
    # Compute number of attempts
    for attempt in range(retries):
        # Save response
        response = requests.get(f"{features_url}?ids={','.join(track_ids)}", headers=headers)

        if response.status_code == 200:
            try:
                return response.json()
            except json.JSONDecodeError as e:
                print("Failed to decode JSON from response:", e)
                return None
        
        elif response.status_code == 502:
            print(f"Attempt {attempt+1} failed with 502 Server Error. Retrying in {delay} seconds...")
            time.sleep(delay)  # Wait before retrying
        else:
            print(f"Failed to fetch audio features: {response.status_code}")
            print("Response content:", response.text)  # To help diagnose the issue
            return None
    
    print("All retry attempts failed.")
    return None

# Function to get all liked songs from my personal list
def get_spotify_liked_songs(username, scope, client_id, client_secret, redirect_uri):
    '''
    Retrieves a list of liked songs from a user's Spotify account along with their audio features.

    Inputs:
    - username: Spotify username of the user.
    - scope: Permissions for accessing Spotify data (e.g., 'user-library-read user-read-private').
    - client_id: The client ID for your application registered with Spotify.
    - client_secret: The client secret for your application registered with Spotify.
    - redirect_uri: The URI to redirect to after a user authorizes an app.

    Outputs:
    - songs_data: A list of dictionaries, each containing details and audio features of each liked song.

    The function authenticates with Spotify, retrieves liked songs, and fetches their audio features.
    '''

    # Make the request
    response = requests.get(tracks_url, headers=headers)

    # Authenticate and get an access token using Spotify's OAuth
    token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)
    headers = {"Authorization": f"Bearer {token}"}

    # Base URL for the Spotify Get User's Saved Tracks endpoint
    tracks_url = "https://api.spotify.com/v1/me/tracks"
    limit = 50  # Maximum number of tracks to retrieve per request
    offset = 0  # Offset for pagination
    songs_data = []  # List to store song data
    all_track_ids = []  # List to store all track IDs for fetching audio features

    while True:
        # Construct the paginated URL with the current limit and offset
        paginated_url = f"{tracks_url}?limit={limit}&offset={offset}"
        response = requests.get(paginated_url, headers=headers)
        
        # Check for a successful response
        if response.status_code != 200:
            print(f"Failed to fetch data: {response.status_code}")
            break

        data = response.json()
        items = data.get('items', [])

        # If no items are returned, end the loop
        if not items:
            print("No more tracks found.")
            break

        # Process each track in the items list
        for song in items:
            track = song.get('track')
            if track:
                track_ids = track['id']
                all_track_ids.append(track_ids)
                track_data = {
                    "Name": track['name'],
                    "Artist": track['artists'][0]['name'],
                    "Track Popularity": track["popularity"]
                }
                songs_data.append(track_data)
                print(f"{track['name']} by {track['artists'][0]['name']}")

        # Check if the number of items is less than the limit, indicating the end of data
        if len(items) < limit:
            break
        offset += limit  # Increment the offset for the next batch of tracks

    # Fetch audio features for all collected track IDs
    audio_features = get_audio_features(token, all_track_ids)
    # Combine the songs data with their audio features
    for song_data, features in zip(songs_data, audio_features['audio_features']):
        song_data.update({
            "Danceability": features['danceability'],
            "Energy": features['energy'],
            "Valence": features['valence'],
            "Tempo": features['tempo'],
            "Loudness": features['loudness']
        })

    # Return the data frame
    return songs_data