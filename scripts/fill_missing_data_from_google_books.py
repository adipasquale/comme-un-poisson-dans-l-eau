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

for ressource in cur.execute("SELECT * FROM ressources WHERE isbn IS NOT NULL AND google_books_json IS NULL").fetchall():
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"isbn:{ressource['isbn']}",
        "maxResults": 1,
        "key": os.getenv("GOOGLE_API_KEY")
    }
    response = requests.get(url, params=params)
    data = response.json()

    if "items" not in data or len(data["items"]) == 0:
        logging.info(f"Could not find {
                     ressource['title']} - {ressource['isbn']}")
        logging.info(data)
        continue

    google_books_json = json.dumps(data["items"][0])
    cur.execute("UPDATE ressources SET google_books_json = ? WHERE isbn = ?",
                (google_books_json, ressource['isbn']))
    con.commit()
