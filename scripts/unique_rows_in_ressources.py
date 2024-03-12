from dotenv import load_dotenv
import logging
from db import get_connection
from collections import Counter

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

ressources = cur.execute(
    "SELECT slug FROM ressources WHERE slug IS NOT NULL").fetchall()
count_by_slugs = Counter([r["slug"] for r in ressources])
duplicates_by_slug = [slug for slug,
                      count in count_by_slugs.items() if count > 1]
logging.info(f"Found {len(duplicates_by_slug)} duplicates based on slugs :")
for slug in duplicates_by_slug:
    logging.info(f" - deleting one ressource for {slug}")
    cur.execute(
        "DELETE FROM ressources WHERE rowid = (SELECT rowid FROM ressources WHERE slug = ? LIMIT 1)", (slug,))
    con.commit()

isbns = [r["isbn"] for r in cur.execute(
    """
        SELECT isbn
        FROM ressources
        WHERE type_ressource = 'livre'
        GROUP BY isbn
        HAVING count(isbn) > 1
    """
).fetchall()]
for isbn in isbns:
    ressources = cur.execute(
        "SELECT rowid, slug, isbn, titre FROM ressources WHERE isbn = ?", (isbn,)).fetchall()
    logging.info(f"Found {len(ressources)} duplicates for isbn {isbn} titre {ressources[0]['titre']}")
    keep = ressources[0]
    for duplicate in ressources[1:]:
        logging.info(f" - merging {duplicate['titre']}")
        cur.execute(
            "UPDATE episodes_to_ressources SET ressource_slug = ? WHERE ressource_slug = ?",
            (keep["slug"], duplicate["slug"])
        )
        cur.execute("DELETE FROM ressources WHERE rowid = ?", (duplicate["rowid"],))
        con.commit()
