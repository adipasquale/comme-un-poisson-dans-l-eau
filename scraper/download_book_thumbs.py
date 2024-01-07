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
    cur.execute("ALTER TABLE ressources ADD COLUMN book_thumb TEXT")
except sqlite3.OperationalError:
    pass

for ressource in cur.execute("SELECT * FROM ressources WHERE kind='book' AND google_books_json IS NOT NULL").fetchall():
    try:
        data = json.loads(ressource["google_books_json"])
    except json.decoder.JSONDecodeError:
        logging.warning(f"could not parse json for {ressource['slug']} #{
                        ressource['video_id']} : {ressource['google_books_json']}")
        continue

    url = data["volumeInfo"].get("imageLinks", {}).get("thumbnail")
    if url is None:
        continue
    ids = [ressource.get(id) or "" for id in ['authors', 'book_title', 'isbn']]
    filename = slugify(" ".join(ids)) + ".jpg"
    path = f"../images/books/{filename}"

    # if os.path.exists(path):
    #     continue

    # logging.info(f"downloading {url} to {path}...")
    # with open(path, "wb") as f:
    #     f.write(requests.get(url).content)

    cur.execute(
        "UPDATE ressources SET book_thumb = ? WHERE slug = ? and video_id = ?",
        (filename, ressource["slug"], ressource["video_id"])
    )
    con.commit()
