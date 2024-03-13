import json
from dotenv import load_dotenv
import logging
from db import get_connection
import requests
import os
from slugify import slugify
import html

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

if not os.getenv("GOOGLE_API_KEY"):
    logging.error("GOOGLE_API_KEY is not set")
    exit(1)


def get_google_books_data(isbn):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"isbn:{isbn}",
        "maxResults": 1,
        "key": os.getenv("GOOGLE_API_KEY")
    }
    response = requests.get(url, params=params)
    data = response.json()
    if "items" not in data or len(data["items"]) == 0:
        logging.info(f"Could not find {isbn} in google books api")
        logging.info(data)
        return None

    return data["items"][0]


def update_and_download_thumb(ressource, google_books_data):
    url = google_books_data["volumeInfo"].get("imageLinks", {}).get("thumbnail")
    if url is None:
        return

    ids = [ressource.get(id) or "" for id in ['authors', 'book_title', 'isbn']]
    filename = slugify(" ".join(ids)) + ".jpg"
    path = os.path.join(os.path.dirname(__file__), "..", "images", "books", filename)

    if not os.path.exists(path):
        logging.info(f"downloading {url} to {path}...")
        with open(path, "wb") as f:
            f.write(requests.get(url).content)

    cur.execute(
        "UPDATE ressources SET livre_image = ? WHERE slug = ?",
        (filename, ressource["slug"])
    )
    con.commit()


def update_metadata(ressource, google_books_data):
    volume_info = google_books_data["volumeInfo"]
    logging.debug(volume_info)
    parsed_description_courte = google_books_data.get("searchInfo", {}).get("textSnippet")
    if parsed_description_courte:
        parsed_description_courte = html.unescape(parsed_description_courte)
    cur.execute(
        """
            UPDATE ressources
            SET
                livre_titre = ?,
                livre_sous_titre = ?,
                auteurs = ?,
                description = ?,
                description_courte = ?,
                date_publication = ?
            WHERE slug = ?
        """,
        (
            ressource["livre_titre"] or volume_info["title"],
            ressource["livre_sous_titre"] or volume_info.get("subtitle"),
            ressource["auteurs"] or ",".join(volume_info["authors"]),
            ressource["description"] or volume_info.get("description"),
            ressource["description_courte"] or parsed_description_courte,
            ressource["date_publication"] or volume_info.get("publishedDate"),
            ressource["slug"]
        )
    )
    con.commit()


for ressource in cur.execute(
    """
        SELECT * FROM ressources
        WHERE type_ressource = 'livre'
        AND isbn IS NOT NULL
        AND (
            livre_image IS NULL
            OR auteurs IS NULL
            OR livre_titre IS NULL
            OR description is NULL
            OR description_courte is NULL
            OR date_publication is NULL
        )
    """).fetchall():
    logging.info(f"fetching google books data for {ressource['isbn']} - {ressource['titre']}")
    google_books_data = get_google_books_data(ressource["isbn"])
    if not google_books_data or not google_books_data.get("volumeInfo"):
        logging.info(f"Could not find {ressource['isbn']} in google books api, skipping...")
        continue
    if not ressource["livre_image"]:
        update_and_download_thumb(ressource, google_books_data)
    update_metadata(ressource, google_books_data)
    print()
