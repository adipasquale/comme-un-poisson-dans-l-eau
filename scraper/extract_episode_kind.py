from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection
import re

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE episodes ADD COLUMN kind TEXT")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    kind = "interview"
    if re.search(r"lecture", episode["title"], re.IGNORECASE):
        kind = "reading"

    logging.info(
        f"updating {episode['title']} with kind {kind}"
    )
    cur.execute(
        "UPDATE episodes SET kind = ? WHERE youtube_id = ?",
        (kind, episode["youtube_id"])
    )
con.commit()
