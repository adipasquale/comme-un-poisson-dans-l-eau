import json
from dotenv import load_dotenv
import sqlite3
import logging
from scripts.db import get_connection
import requests
import os

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

for ressource in cur.execute("SELECT * FROM ressources WHERE type_ressource='livre' AND isbn IS NOT NULL AND google_books_json IS NOT NULL AND google_books_json != '' AND (description IS NULL OR description = '')").fetchall():
    data = json.loads(ressource["google_books_json"])
    description = data["volumeInfo"].get("description") or None
    if not description:
        continue
    logging.info(
        f"updating {ressource['titre']}  with description {description[:50]}..."
    )
    cur.execute(
        "UPDATE ressources SET description = ? WHERE isbn = ?",
        (
            description,
            ressource["isbn"]
        )
    )
    con.commit()
