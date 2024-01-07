import path from 'path'
import sqlite3 from 'sqlite3'
import { open } from 'sqlite'

export default async function () {
  const db = await open({ filename: 'commeunpoissondansleau.db', driver: sqlite3.Database })
  const all = await db.all('SELECT * FROM ressources')
  const livres = await db.all('SELECT * FROM ressources WHERE kind="livre"')
  await db.close()

  return { all, livres }
}
