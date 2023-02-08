import requests
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint
from dotenv import load_dotenv
import os
load_dotenv()

# Check whether .env exist
try:
    YOUR_CLIENT_ID = os.environ['CLIENT_ID']
    YOUR_CLIENT_SECRET = os.environ['CLIENT_SECRET']
except KeyError:
    print("One of the environment variables CLIENT_ID or CLIENT_SECRET is not set. Exiting...")
    pass

# You can get CLIENT_ID and CLIENT_SECRET from https://developer.spotify.com/dashboard/applications
CLIENT_ID = YOUR_CLIENT_ID
CLIENT_SECRET = YOUR_CLIENT_SECRET

print(YOUR_CLIENT_ID)
print(YOUR_CLIENT_SECRET)

# Put this url to your Redirect URIs in https://developer.spotify.com/dashboard/applications
REDIRECT_URL = "https://example.com/callback/"


date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
billboard = response.text

soup = BeautifulSoup(billboard, "html.parser")
songs = soup.find_all(name="li", class_="lrv-u-width-100p")
song_title = []

for title in songs:
    if title.find(name="h3") is None:
        pass
    else:
        song_title.append(title.find(name="h3").getText().strip())

print(song_title)

print(len(song_title))


sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URL,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

pp = pprint.PrettyPrinter(indent=4)
pp.pprint(sp.user_playlists(user=user_id))

song_uris = []
year = date.split("-")[0]

for song in song_title:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped.")

playlist = sp.user_playlist_create(user=user_id, name=f"Billboard Song From {date}", public=False)
print(playlist)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)