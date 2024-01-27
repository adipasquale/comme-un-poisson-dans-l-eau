import os
import json
from db import get_connection
from dotenv import load_dotenv

CURDIR = os.path.dirname(os.path.realpath(__file__))

load_dotenv()
con = get_connection()
cur = con.cursor()


for json_filename in os.listdir(os.path.join(CURDIR, '../audio/')):
    if not json_filename.endswith('.transcript.raw.json'):
        continue

    slug = json_filename[:-20]
    row = cur.execute("SELECT interviewee FROM episodes WHERE slug = ?", (slug,)).fetchone()

    print("--------------------\n")
    print(json_filename)
    md_filename = f"{slug}.md"
    with open(os.path.join(CURDIR, "../audio/", json_filename), 'r') as json_file, \
            open(os.path.join(CURDIR, "../11ty_input/transcripts/", md_filename), 'w') as md_file:

        md_file.write(f"---\ntags: transcript\nslug: {slug}\n---\n\n")
        for segment in json.load(json_file)["segments"]:
            speaker = segment["speaker"]
            if speaker == "SPEAKER_00":
                speaker = "Victor Duran-Le Peuch"
            elif speaker == "SPEAKER_01" and row["interviewee"]:
                speaker = row["interviewee"]
            else:
                speaker = f"Intervenant {int(speaker[-2:]) + 1}"
            md_file.write(f"**{speaker}** : {segment['text']}\n\n")
        print(f"written to {md_filename}")
