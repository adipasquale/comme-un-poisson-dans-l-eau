import requests
import os
from dotenv import load_dotenv
import json
import logging
from scripts.db import get_connection
from slugify import slugify

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

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

episodes = list(cur.execute("SELECT * FROM episodes").fetchall())

def parse_youtube_json_to_episode(youtube_json):
    titre = youtube_json["snippet"]["title"]
    raw_description = youtube_json["snippet"]["description"]
    description_sections = raw_description.split("\n___")
    thumbs = data["snippet"]["thumbnails"]
    return {
        "youtube_id" : youtube_json["id"],
        "youtube_json" : json.dumps(youtube_json),
        "titre" : titre,
        "slug" : slugify(titre),
        "date_publication" : youtube_json["snippet"]["publishedAt"],
        "poster_filename" : thumbs.get("standard", thumbs.get("high", {})).get("url"),
        "description" : description_sections[0].strip(),
        "type_episode" : "entretien",
    }


next_page_token = None
while True:
    if next_page_token:
        videos_url += f"&pageToken={next_page_token}"

    logging.info(f"Requesting {videos_url}...")
    response = requests.get(videos_url)
    data = response.json()

    logging.info(f"Inserting {len(data['items'])} videos into the db...")
    for video in data["items"]:
        parsed_episode = parse_youtube_json_to_episode(video)
        if any(episode["titre"] == parsed_episode["titre"] for episode in episodes):
            continue
        logging.info(f"Importing new episode {parsed_episode['titre']}...")
        cur.execute(
            """
                INSERT INTO episodes (
                    youtube_id,
                    youtube_json,
                    titre,
                    slug,
                    date_publication,
                    poster_filename,
                    description,
                    type_episode
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                parsed_episode["youtube_id"],
                parsed_episode["youtube_json"],
                parsed_episode["titre"],
                parsed_episode["slug"],
                parsed_episode["date_publication"],
                parsed_episode["poster_filename"],
                parsed_episode["description"],
                parsed_episode["type_episode"]
            ))
        con.commit()

    if "nextPageToken" in data:
        next_page_token = data["nextPageToken"]
    else:
        break
