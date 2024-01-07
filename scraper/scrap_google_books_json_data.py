import json
from dotenv import load_dotenv
import sqlite3
import logging
import os
import requests

from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE ressources ADD COLUMN isbn TEXT")
    cur.execute("ALTER TABLE ressources ADD COLUMN google_books_json TEXT")
except sqlite3.OperationalError:
    pass

for ressource in cur.execute("SELECT * FROM ressources WHERE isbn IS NULL AND (kind IS NULL OR kind = ?)", ("livre", )).fetchall():
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": ressource["title"],
        "maxResults": 3,
        "key": os.getenv("GOOGLE_API_KEY")
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "items" not in data:
        logging.info(f"Could not find {ressource['title']}")
        logging.info(data)
        continue
    elif len(data["items"]) > 0:
        google_books_json = json.dumps(data["items"][0])
        isbn = None
        for id in data["items"][0]["volumeInfo"]["industryIdentifiers"]:
            if id["type"] == "ISBN_13":
                isbn = id["identifier"]
        logging.info(f"Found {isbn} for {ressource['title']}")
        cur.execute("UPDATE ressources SET google_books_json = ?, isbn = ? WHERE slug = ? and video_id = ?",
                    (google_books_json, isbn, ressource["slug"], ressource["video_id"]))

        con.commit()
