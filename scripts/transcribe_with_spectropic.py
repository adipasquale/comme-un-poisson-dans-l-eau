import requests
from dotenv import load_dotenv
import os
from flask import Flask, request
import threading
import sys
from db import get_connection
load_dotenv()
con = get_connection()
cur = con.cursor()

webhooks_host = sys.argv[1]
if not webhooks_host:
    raise Exception("call the script with a webhooks host like https://38bfefb64c193258162af21c496c0ce8.loophole.site")


existing_transcript_file_names = [
    file_name[0:-20] for file_name in os.listdir('audio/') if file_name.endswith('.transcript.raw.json')
]

audio_file_names = sorted([
    f for f in os.listdir('audio/')
    if f.endswith('.webm')
    and f[:-5] not in existing_transcript_file_names
])[0:1]

print(f"file names : {audio_file_names}")

app = Flask(__name__)
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=23336, debug=True, use_reloader=False)).start()


CURDIR = os.path.dirname(os.path.realpath(__file__))


@app.route("/transcript_result/<int:index>", methods=["POST"])
def transcript_result_received(index):
    print(f"transcript result received for file {index} : {audio_file_names[index]}")
    transcript_file_path = os.path.join(
        CURDIR,
        '../audio',
        audio_file_names[index][:-5] + '.transcript.raw.json'
    )
    print(f"writing transcript to {transcript_file_path}...")
    with open(transcript_file_path, 'w') as f:
        f.write(request.get_data().decode('utf-8'))
    return "ok"


vocab = [
    "antispécisme",
    "spécisme",
    "Victor Duran-Le Peuch",
    "L’amorce"
]
vocab += [r["interviewee"] for r in cur.execute("SELECT interviewee FROM episodes").fetchall()]


for index, file_name in enumerate(audio_file_names):
    webhook_url = f"{webhooks_host}/transcript_result/{index}"
    print(f"enqueuing transcript for file {file_name} with webhook {webhook_url}...")
    response = requests.request(
        "POST",
        "https://api.spectropic.ai/v1/transcripts",
        json={
            "language": "fr",
            "numSpeakers": 2,
            "vocabulary": ", ".join(vocab),
            "webhook": webhook_url,
            "url": f"https://comme-un-poisson-dans-l-eau.s3.fr-par.scw.cloud/{file_name}"
        },
        headers={
            "Authorization": f"Bearer {os.getenv('SPECTROPIC_API_KEY')}",
            "Content-Type": "application/json"
        }
    )
