import json
from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection
import requests
import os
from slugify import slugify

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE episodes ADD COLUMN poster_filename TEXT")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])

    thumbs = data["snippet"]["thumbnails"]
    url = thumbs.get("standard", thumbs.get("high", {})).get("url")

    if url is None:
        continue

    filename = f"{episode['slug']}.jpg"
    path = f"../images/episodes/{filename}"

    if os.path.exists(path):
        continue

    logging.info(f"downloading {url} to {path}...")
    with open(path, "wb") as f:
        f.write(requests.get(url).content)

    cur.execute(
        "UPDATE episodes SET poster_filename = ? WHERE youtube_id = ?",
        (filename, episode["youtube_id"])
    )
    con.commit()
