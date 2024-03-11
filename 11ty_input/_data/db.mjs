import sqlite3 from 'sqlite3'
import { open } from 'sqlite'
import { fileURLToPath } from 'url';
import path from 'path';


export default async function () {
  const dbPath = path.resolve(fileURLToPath(import.meta.url), '../../../commeunpoissondansleau.db');
  const db = await open({ filename: dbPath, driver: sqlite3.Database })
  const ressources = await db.all(`
    SELECT ressources.*, GROUP_CONCAT(episodes_to_ressources.episode_slug) as episode_slugs
    FROM ressources
    LEFT JOIN episodes_to_ressources ON ressources.slug = episodes_to_ressources.ressource_slug
    -- WHERE type_ressource="livre"
    GROUP BY ressources.slug
    ORDER BY COUNT(episodes_to_ressources.episode_slug) DESC
  `)

  const episodes = await db.all(`
    SELECT episodes.*, GROUP_CONCAT(episodes_to_ressources.ressource_slug) as ressource_slugs
    FROM episodes
    LEFT JOIN episodes_to_ressources ON episodes.slug = episodes_to_ressources.episode_slug
    GROUP BY episodes.slug
    ORDER BY date_publication ASC
  `)

  const episodeBySlug = episodes.reduce((acc, episode) => {
    acc[episode.slug] = episode
    return acc
  }, {})

  ressources.forEach(ressource => {
    ressource.episodes = ressource.episode_slugs?.split(',')?.map(slug => episodeBySlug[slug])
  })

  const ressourcesBySlug = ressources.reduce((acc, ressource) => {
    acc[ressource.slug] = ressource
    return acc
  }, {})

  episodes.forEach(episode => {
    episode.livres = []
    episode.ressources = []
    for (const slug of episode.ressource_slugs?.split(',') || []) {
      const ressource = ressourcesBySlug[slug]
      if (ressource.type_ressource === 'livre')
        episode.livres.push(ressource)
      else
        episode.ressources.push(ressource)
    }
  })

  const livres = ressources.filter(ressource => ressource.type_ressource === 'livre')
  const entretiens = episodes.filter(episode => episode.type_episode === 'entretien')
  const lectures = episodes.filter(episode => episode.type_episode === 'lecture')
  const episodes_speciaux = episodes.filter(episode => episode.type_episode === 'special')

  await db.close()

  return { ressources, episodes, entretiens, lectures, episodes_speciaux, livres }
}
