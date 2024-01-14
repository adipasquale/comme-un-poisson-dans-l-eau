import sqlite3 from 'sqlite3'
import { open } from 'sqlite'
import { fileURLToPath } from 'url';
import path from 'path';


export default async function () {
  const dbPath = path.resolve(fileURLToPath(import.meta.url), '../../../commeunpoissondansleau.db');
  const db = await open({ filename: dbPath, driver: sqlite3.Database })
  const ressources = await db.all('SELECT * FROM ressources')
  const books = await db.all('SELECT * FROM ressources WHERE kind="book"')

  const episodes = await db.all(`
    SELECT episodes.*, GROUP_CONCAT(episodes_to_ressources.ressource_slug) as ressource_slugs
    FROM episodes
    LEFT JOIN episodes_to_ressources ON episodes.slug = episodes_to_ressources.episode_slug
    GROUP BY episodes.slug
    ORDER BY youtube_published_at DESC
  `)
  const ressourcesBySlug = ressources.reduce((acc, ressource) => {
    acc[ressource.slug] = ressource
    return acc
  }, {})
  episodes.forEach(episode => {
    episode.ressources = episode.ressource_slugs?.split(',')?.map(slug => ressourcesBySlug[slug])
  })
  const interviews = episodes.filter(episode => episode.kind === 'interview')
  const readings = episodes.filter(episode => episode.kind === 'reading')
  const specials = episodes.filter(episode => episode.kind === 'special')


  await db.close()

  return { ressources, interviews, readings, specials, books }
}
