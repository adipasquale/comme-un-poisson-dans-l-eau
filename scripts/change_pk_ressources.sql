-- ressources table fields:
slug TEXT YES NULL youtube_id TEXT YES NULL title TEXT YES NULL kind TEXT YES NULL url TEXT YES NULL url_domain TEXT YES NULL isbn TEXT YES NULL google_books_json TEXT YES NULL book_thumb TEXT YES NULL authors TEXT YES NULL book_title TEXT YES NULL book_subtitle TEXT YES NULL -- Alter table to change primary key
PRAGMA foreign_keys = off;

BEGIN TRANSACTION;

-- Create a new table with the desired schema
CREATE TABLE ressources_new (
  slug TEXT PRIMARY KEY,
  title TEXT,
  kind TEXT,
  url TEXT,
  url_domain TEXT,
  isbn TEXT,
  google_books_json TEXT,
  book_thumb TEXT,
  authors TEXT,
  book_title TEXT,
  book_subtitle TEXT
);

-- Copy the data from the old table to the new table
INSERT INTO
  ressources_new
SELECT
  slug,
  title,
  kind,
  url,
  url_domain,
  isbn,
  google_books_json,
  book_thumb,
  authors,
  book_title,
  book_subtitle
FROM
  ressources;

-- Drop the old table
DROP TABLE ressources;

-- Rename the new table to the original table name
ALTER TABLE
  ressources_new RENAME TO ressources;

COMMIT;

PRAGMA foreign_keys = on;
