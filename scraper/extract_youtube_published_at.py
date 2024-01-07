import json
from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE episodes ADD COLUMN youtube_published_at DATE")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])
    published_at = data["snippet"]["publishedAt"]
    logging.info(
        f"updating {episode['youtube_id']} with published_at {published_at}"
    )
    cur.execute(
        "UPDATE episodes SET youtube_published_at = ? WHERE youtube_id = ?",
        (
            published_at,
            episode["youtube_id"]
        )
    )
