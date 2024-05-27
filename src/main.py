# Main file
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
from utils import *
from dotenv import load_dotenv
import os

# Take environment variables from .env
load_dotenv()  

# Define the credentials
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')
redirect_uri = "http://localhost:8080/callback"
scope = 'user-library-read'
username = 'ernakuginyte' 
# Create a token
token = util.prompt_for_user_token(username,
                                   scope,
                                   client_id=client_id,
                                   client_secret=client_secret,
                                   redirect_uri=redirect_uri)

# Get a data frame of liked songs
liked_songs = get_spotify_liked_songs(username, scope, client_id, client_secret, redirect_uri)




