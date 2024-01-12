from dotenv import load_dotenv
import logging
from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

cur.execute("DELETE FROM episodes_to_ressources")
con.commit()

sql = """
SELECT
    ressources.slug AS ressource_slug,
    episodes.slug AS episode_slug
FROM ressources
LEFT JOIN episodes ON ressources.youtube_id = episodes.youtube_id
"""

for row in cur.execute(sql).fetchall():
    cur.execute(
        "INSERT INTO episodes_to_ressources (episode_slug, ressource_slug) VALUES (?, ?)",
        (row["episode_slug"], row["ressource_slug"])
    )
    con.commit()
