import requests
import os
from dotenv import load_dotenv
import json
import logging
from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS ressources")
cur.execute("DROP TABLE IF EXISTS episodes")
cur.execute(
    "CREATE TABLE videos (youtube_id TEXT, youtube_json TEXT, title TEXT)")

channel_id = "UCfzKqH_Ft8_8yFrGzG3x9-g"
api_key = os.getenv("GOOGLE_API_KEY")

# Make a request to the YouTube Data API to get the channel's uploads playlist ID
channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={
    channel_id}&key={api_key}"
response = requests.get(channel_url)
data = response.json()
uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Make a request to the YouTube Data API to get the videos from the uploads playlist
videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={
    uploads_playlist_id}&key={api_key}&maxResults=50&sort=date"

next_page_token = None
while True:
    if next_page_token:
        videos_url += f"&pageToken={next_page_token}"

    logging.info(f"Requesting {videos_url}...")
    response = requests.get(videos_url)
    data = response.json()

    logging.info(f"Inserting {len(data['items'])} videos into the db...")
    for video in data["items"]:
        title = video["snippet"]["title"]
        cur.execute(
            "INSERT INTO videos (youtube_id, youtube_json, title) VALUES (?, ?, ?)", (video["id"], json.dumps(video), title))
        con.commit()

    if "nextPageToken" in data:
        next_page_token = data["nextPageToken"]
    else:
        break
