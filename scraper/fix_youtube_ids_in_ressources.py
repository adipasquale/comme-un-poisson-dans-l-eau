from dotenv import load_dotenv
import logging
from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    cur.execute(
        "UPDATE ressources SET youtube_id = ? WHERE youtube_id = ?",
        (episode["youtube_id"], episode["youtube_bad_id"])
    )
    con.commit()
