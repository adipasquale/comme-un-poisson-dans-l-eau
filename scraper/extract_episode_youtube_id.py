from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection
from slugify import slugify
import json

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE episodes ADD COLUMN youtube_id TEXT")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])
    youtube_id = data["snippet"]["resourceId"]["videoId"]
    logging.info(
        f"updating {episode['youtube_bad_id']} with youtube_id {youtube_id}"
    )
    cur.execute(
        "UPDATE episodes SET youtube_id = ? WHERE youtube_bad_id = ?",
        (youtube_id, episode["youtube_bad_id"])
    )
con.commit()
