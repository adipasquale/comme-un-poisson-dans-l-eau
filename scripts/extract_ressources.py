import json
from dotenv import load_dotenv
import logging
from urllib.parse import urlparse
import re
from slugify import slugify
from db import get_connection

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

cur = con.cursor()
cur.execute("DROP TABLE IF EXISTS ressources")
cur.execute("""
    CREATE TABLE ressources (
        slug TEXT,
        youtube_id TEXT,
        title TEXT,
        kind TEXT,
        url TEXT,
        url_domain TEXT,
        PRIMARY KEY (slug, youtube_id)
    )
""")


def extract_ressources(description):
    ressources = []
    for line in description.split("\n"):
        if line.startswith("- "):
            ressources.append(line[2:])
    return ressources


for episode in cur.execute("SELECT * FROM episodes").fetchall():
    youtube_json = json.loads(episode["youtube_json"])
    ressources = extract_ressources(youtube_json["snippet"]["description"])
    logging.info(f"Inserting {len(ressources)} ressources into the db...")
    for ressource in ressources:
        url = None
        words = ressource.split(" ")
        for word in words:
            if word.startswith("https://"):
                url = word
                words.remove(word)
                break
            elif word.startswith("(https://"):
                url = word[1:-2]
                words.remove(word)
                break

        url_domain = None
        if url:
            parsed_url = urlparse(url)
            url_domain = parsed_url.hostname

        title = " ".join(words).strip(" :")
        kind = None
        if "(livre)" in title:
            kind = "livre"
            title = title.replace("(livre)", "").strip()
        elif "(documentaire)" in title:
            kind = "documentary"
            title = title.replace("(documentaire)", "").strip()
        elif url and "podcast" in title:
            kind = "podcast"
        elif url and "youtube" in url:
            kind = "video"
        elif url and "wikipedia" in url:
            kind = "wikipedia"
        elif url:
            kind = "lien"
        elif re.match(r"concept", title, re.IGNORECASE):
            kind = "concept"

        slug = slugify(title or url)

        cur.execute(
            "INSERT INTO ressources (slug, youtube_id, title, url, url_domain, kind) VALUES (?, ?, ?, ?, ?, ?)",
            (slug, video["id"], title, url, url_domain, kind)
        )
        con.commit()
