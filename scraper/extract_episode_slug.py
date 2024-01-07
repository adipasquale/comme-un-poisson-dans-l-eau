from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection
from slugify import slugify

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE episodes ADD COLUMN slug TEXT")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    slug = slugify(episode["title"])
    logging.info(
        f"updating {episode['youtube_id']} with slug {slug}"
    )
    cur.execute(
        "UPDATE episodes SET slug = ? WHERE youtube_id = ?",
        (slug, episode["youtube_id"])
    )
con.commit()
