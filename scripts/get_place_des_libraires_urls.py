from urllib.parse import urlparse
from dotenv import load_dotenv
import logging
from db import get_connection
import requests

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

for ressource in cur.execute("SELECT * FROM ressources WHERE kind = 'book' AND isbn IS NOT NULL AND url is NULL").fetchall():
    url = f"https://www.placedeslibraires.fr/detailrewrite.php?ean={ressource['isbn']}"
    print(f"\nFetching {url}...")
    r = requests.get(url, allow_redirects=True, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/92.0.4515.159 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
    })
    new_url = r.url
    if new_url == url:
        print("No redirect")
        continue
    print(f"url after redirect : {new_url}")
    path = urlparse(new_url).path
    if path.startswith("/livre/"):
        new_url = f"https://www.placedeslibraires.fr/{path}"
        print(f"storing ressource url : {new_url}")
        cur.execute("UPDATE ressources SET url = ? WHERE slug = ?",
                    (new_url, ressource["slug"]))
        con.commit()
