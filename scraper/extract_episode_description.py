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
    cur.execute("ALTER TABLE episodes ADD COLUMN description TEXT")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])
    raw_description = data["snippet"]["description"]

    # Cut description into sections delimited by lines starting with ___
    sections = raw_description.split("\n___")
    description = sections[0].strip()

    logging.info(
        f"updating {episode['youtube_id']} with description..."
    )
    cur.execute(
        "UPDATE episodes SET description = ? WHERE youtube_id = ?",
        (description, episode["youtube_id"])
    )
con.commit()
