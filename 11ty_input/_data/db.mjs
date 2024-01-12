import sqlite3 from 'sqlite3'
import { open } from 'sqlite'
import { fileURLToPath } from 'url';
import path from 'path';


export default async function () {
  const dbPath = path.resolve(fileURLToPath(import.meta.url), '../../../commeunpoissondansleau.db');
  const db = await open({ filename: dbPath, driver: sqlite3.Database })
  const ressources = await db.all('SELECT * FROM ressources')
  const books = await db.all('SELECT * FROM ressources WHERE kind="book"')

  const interviews = await db.all('SELECT * FROM episodes WHERE kind = "interview" ORDER BY youtube_published_at DESC')
  const readings = await db.all('SELECT * FROM episodes WHERE kind = "reading" ORDER BY youtube_published_at DESC')
  const specials = await db.all('SELECT * FROM episodes WHERE kind = "special" ORDER BY youtube_published_at DESC')

  await db.close()

  return { ressources, interviews, readings, specials, books }
}
