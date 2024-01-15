import sqlite3 from 'sqlite3'
import { open } from 'sqlite'
import { fileURLToPath } from 'url';
import path from 'path';


export default async function () {
  const dbPath = path.resolve(fileURLToPath(import.meta.url), '../../../commeunpoissondansleau.db');
  const db = await open({ filename: dbPath, driver: sqlite3.Database })
  const ressources = await db.all('SELECT * FROM ressources')
  const books = await db.all(`
    SELECT ressources.*, GROUP_CONCAT(episodes_to_ressources.episode_slug) as episode_slugs
    FROM ressources
    LEFT JOIN episodes_to_ressources ON ressources.slug = episodes_to_ressources.ressource_slug
    WHERE kind="book"
    GROUP BY ressources.slug
    ORDER BY COUNT(episodes_to_ressources.episode_slug) DESC
  `)

  const episodes = await db.all(`
    SELECT episodes.*, GROUP_CONCAT(episodes_to_ressources.ressource_slug) as ressource_slugs
    FROM episodes
    LEFT JOIN episodes_to_ressources ON episodes.slug = episodes_to_ressources.episode_slug
    GROUP BY episodes.slug
    ORDER BY youtube_published_at DESC
  `)

  const episodeBySlug = episodes.reduce((acc, episode) => {
    acc[episode.slug] = episode
    return acc
  }, {})
  books.forEach(book => {
    book.episodes = book.episode_slugs?.split(',')?.map(slug => episodeBySlug[slug])
  })

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

  return { ressources, episodes, interviews, readings, specials, books }
}
