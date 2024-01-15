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

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])
    published_at_str = data["snippet"]["publishedAt"]
    published_at = published_at_str.split("T")[0]

    cur.execute(
        "UPDATE episodes SET youtube_published_at = ? WHERE slug = ?",
        (published_at, episode["slug"])
    )
    con.commit()
