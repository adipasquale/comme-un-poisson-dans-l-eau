from dotenv import load_dotenv
import logging
from db import get_connection
import json

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

for episode in cur.execute("SELECT * FROM episodes WHERE credits IS NULL").fetchall():
    logging.info(f"Extracting credits for episode {episode['titre']}")
    credits = None
    youtube_data = json.loads(episode["youtube_json"])
    splitted = youtube_data["snippet"]["description"].split("CRÉDITS")
    if len(splitted) < 2:
        logging.warning(f"Could not find credits for episode {episode['titre']}")
        continue
    credits = splitted[1].strip()
    cur.execute("UPDATE episodes SET credits = ? WHERE slug = ?", (credits, episode["slug"]))
    con.commit()
