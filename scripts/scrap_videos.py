import requests
import os
from dotenv import load_dotenv
import json
import logging
from scripts.db import get_connection
from slugify import slugify
from datetime import datetime
import re
from urllib.parse import urlparse

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

channel_id = "UCfzKqH_Ft8_8yFrGzG3x9-g"
api_key = os.getenv("GOOGLE_API_KEY")

# Make a request to the YouTube Data API to get the channel's uploads playlist ID
channel_url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={api_key}"
response = requests.get(channel_url)
data = response.json()
uploads_playlist_id = data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

# Make a request to the YouTube Data API to get the videos from the uploads playlist
videos_url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId={uploads_playlist_id}&key={api_key}&maxResults=50&sort=date"

episodes = list(cur.execute("SELECT * FROM episodes ORDER BY date_publication DESC").fetchall())
most_recent_published_at = datetime.fromisoformat(episodes[0]["date_publication"]).date()


class RessourceParser(object):
    def __init__(self, text):
        self.text = text
        self.url = None

    def parse(self):
        self.parse_url_and_titre()
        self.parse_type()
        return {
            "titre": self.titre,
            "url": self.url,
            "url_domain": self.url and urlparse(self.url).hostname,
            "type_ressource": self.type,
            "slug": slugify(self.titre or self.url)
        }

    def parse_url_and_titre(self):
        words = self.text.split(" ")
        for word in words:
            if word.startswith("https://"):
                self.url = word
                words.remove(word)
                break
            elif word.startswith("(https://"):
                self.url = word[1:-2]
                words.remove(word)
                break
        self.titre = " ".join(words).strip(" :")

    def parse_type(self):
        self.type = None
        if "(livre)" in self.titre:
            self.type = "livre"
            self.titre = self.titre.replace("(livre)", "").strip()
        elif "(documentaire)" in self.titre:
            self.type = "documentaire"
            self.titre = self.titre.replace("(documentaire)", "").strip()
        elif self.url and "podcast" in self.titre:
            self.type = "podcast"
        elif self.url and "youtube" in self.url:
            self.type = "video"
        elif self.url:
            self.type = "lien"
        elif re.match(r"concept", self.titre, re.IGNORECASE):
            self.type = "concept"


def parse_youtube_json_to_ressources(youtube_json):
    ressources = []
    sections = youtube_json["snippet"]["description"].split("\n___")
    if len(sections) < 2:
        return ressources
    for line in youtube_json["snippet"]["description"].split("\n___")[1].split("\n"):
        if line.startswith("- "):
            ressources.append(RessourceParser(line[2:]).parse())
    return ressources


def parse_youtube_json_to_episode(youtube_json):
    titre = youtube_json["snippet"]["title"]
    return {
        "youtube_id": youtube_json["snippet"]["resourceId"]["videoId"],
        "youtube_json": json.dumps(youtube_json),
        "titre": titre,
        "slug": slugify(titre),
        "date_publication": datetime.fromisoformat(youtube_json["snippet"]["publishedAt"]).replace(tzinfo=None).date(),
        "poster_filename": slugify(titre) + ".jpg",
        "description": youtube_json["snippet"]["description"].split("\n___")[0].strip(),
        "type_episode": "entretien",
    }


def download_episode_thumb(youtube_json, episode):
    thumbs = youtube_json["snippet"]["thumbnails"]
    url = thumbs.get("standard", thumbs.get("high", {})).get("url")
    path = os.path.join(os.path.dirname(__file__), "..", "images", "episodes", episode["poster_filename"])
    if os.path.exists(path):
        return
    logging.info(f"downloading {url} to {path}...")
    with open(path, "wb") as f:
        f.write(requests.get(url).content)


def import_episode(youtube_json):
    parsed_episode = parse_youtube_json_to_episode(youtube_json)
    ressources = parse_youtube_json_to_ressources(youtube_json)
    if parsed_episode["date_publication"] < most_recent_published_at:
        return
    if any(episode["titre"] == parsed_episode["titre"] for episode in episodes):
        return
    logging.info(f"Importing new episode : {parsed_episode['titre']}")
    download_episode_thumb(youtube_json, parsed_episode)
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
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
    for ressource in ressources:
        existing_ressource = cur.execute("SELECT * FROM ressources WHERE slug = ?", (ressource['slug'],)).fetchone()
        if existing_ressource:
            logging.info(f"Ressource {ressource['type_ressource']} {ressource['titre']} already exists")
        else:
            logging.info(
                f"Inserting new ressource : {ressource['type_ressource']} - {ressource['titre']} - {ressource['url']}")
            cur.execute(
                """
                    INSERT INTO ressources (
                        slug,
                        titre,
                        type_ressource,
                        url,
                        url_domain
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    ressource["slug"],
                    ressource["titre"],
                    ressource["type_ressource"],
                    ressource["url"],
                    ressource["url_domain"]
                )
            )
        cur.execute(
            """
                INSERT INTO episodes_to_ressources (
                    episode_slug,
                    ressource_slug
                ) VALUES (?, ?)
        """, (
                parsed_episode["slug"],
                ressource["slug"]
            )
        )
    con.commit()
    print()


next_page_token = None
while True:
    if next_page_token:
        videos_url += f"&pageToken={next_page_token}"

    logging.info(f"Requesting {videos_url}...")
    response = requests.get(videos_url)
    data = response.json()

    for youtube_json in data["items"]:
        import_episode(youtube_json)

    if "nextPageToken" in data:
        next_page_token = data["nextPageToken"]
    else:
        break
