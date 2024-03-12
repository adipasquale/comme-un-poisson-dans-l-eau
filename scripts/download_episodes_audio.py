import json
from dotenv import load_dotenv
import sqlite3
import logging
from db import get_connection
import requests
import os
from pytube import YouTube

load_dotenv()
logging.basicConfig(level=logging.INFO)
con = get_connection()
cur = con.cursor()

try:
    cur.execute("ALTER TABLE ressources ADD COLUMN audio_filename TEXT")
except sqlite3.OperationalError:
    pass

for episode in cur.execute("SELECT * FROM episodes").fetchall():
    data = json.loads(episode["youtube_json"])

    filename_without_ext = episode["slug"] + ".webm"
    path = f"../audio/{filename_without_ext}"

    video_url = f"https://www.youtube.com/watch?v={episode['youtube_id']}"
    yt = YouTube(video_url)
    audio_stream = yt.streams.filter(
        only_audio=True, file_extension="webm"
    ).first()

    if not audio_stream:
        logging.info(f"Skipping {episode['slug']}")
        continue

    logging.info(f"Downloading {episode['slug']} audio stream {audio_stream}")
    path = audio_stream.download(
        output_path="../audio", filename=filename_without_ext)
    filename = os.path.basename(path)
    logging.info(f"Downloaded to {path}")

    cur.execute(
        "UPDATE ressources SET audio_filename = ? WHERE youtube_id = ?",
        (filename, episode["youtube_id"])
    )
    con.commit()
