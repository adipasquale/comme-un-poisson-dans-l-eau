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
    cur.execute("ALTER TABLE episodes ADD COLUMN audio_filename TEXT")
except sqlite3.OperationalError:
    pass

for row in cur.execute(
    """
        SELECT episodes.slug, episodes.title, ressources.audio_filename
        FROM episodes
        INNER JOIN episodes_to_ressources ON episodes_to_ressources.episode_slug = episodes.slug
        INNER JOIN ressources ON episodes_to_ressources.ressource_slug = ressources.slug
        GROUP BY episodes.slug;
    """).fetchall():

    cur.execute("UPDATE episodes SET audio_filename = ? WHERE slug = ?",
                (row["audio_filename"], row["slug"]))
    con.commit()
