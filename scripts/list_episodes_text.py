from urllib.parse import urlparse
from dotenv import load_dotenv
import logging
from db import get_connection
import json

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()


def extract_ressources(description):
    ressources = []
    for line in description.split("\n"):
        if line.startswith("- "):
            ressources.append(line[2:])
    return ressources


for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])
    description = data["snippet"]["description"]
    ressources = extract_ressources(description)
    if not ressources:
        continue
    print(f"# {episode['title']}")
    print(f"{episode['slug']}\n")
    print("\n".join(ressources))
    print("\n------\n")
