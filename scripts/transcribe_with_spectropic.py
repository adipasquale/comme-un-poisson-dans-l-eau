from dotenv import load_dotenv
from db import get_connection
import logging
import argparse
import sys
import threading
from flask import Flask, request
import os
import requests

load_dotenv()

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

con = get_connection()
cur = con.cursor()

parser = argparse.ArgumentParser(description='Transcribe audio files.')
parser.add_argument('--webhooks_host', required=True, type=str, help='Webhooks host URL')
parser.add_argument('--limit', default=1, type=int, help='Limit the number of files to transcribe')
parser.add_argument('--disable_dry_run', action='store_true', help='Actually run the requests, disable dry run')
args = parser.parse_args()

if not os.getenv('SPECTROPIC_API_KEY'):
    raise Exception("SPECTROPIC_API_KEY env var is not set")

if not args.webhooks_host:
    raise Exception("call the script with a webhooks host like https://38bfefb64c193258162af21c496c0ce8.loophole.site")

existing_transcript_file_names = [
    file_name[0:-20] for file_name in os.listdir('audio/') if file_name.endswith('.transcript.raw.json')
]

audio_file_names = list(reversed(sorted([
    f for f in os.listdir('audio/')
    if f.endswith('.webm')
    and f[:-5] not in existing_transcript_file_names
])))[:args.limit]
logger.debug(f"will transcribe audio files :")
for file_name in audio_file_names:
    logger.debug(f"- {file_name}")

vocab = [
    "antispécisme",
    "spécisme",
    "Victor Duran-Le Peuch",
    "L’amorce"
] + list(set([
    r["nom_invité"]
    for r in cur.execute("SELECT nom_invité FROM episodes WHERE nom_invité IS NOT NULL").fetchall()
]))

logger.debug("using vocab:")
for word in vocab:
    logger.debug(f"- {word}")

CURDIR = os.path.dirname(os.path.realpath(__file__))

transcript_file_paths = [
    os.path.join(
        CURDIR,
        '../audio',
        audio_file_name[:-5] + '.transcript.raw.json'
    )
    for audio_file_name in audio_file_names
]
logger.debug(f"will write transcript files to:")
for path in transcript_file_paths:
    logger.debug(f"- {path}")

headers = {
    "Authorization": f"Bearer {os.getenv('SPECTROPIC_API_KEY')}",
    "Content-Type": "application/json"
}

requests_params = [
    {
        "language": "fr",
        "numSpeakers": 2,
        "vocabulary": ", ".join(vocab),
        "webhook": f"https://webhook.site/45fdbc67-1ff0-4162-bb16-a644d9dd46e0",
        "url": f"https://comme-un-poisson-dans-l-eau.s3.fr-par.scw.cloud/{file_name}"
    }
    for index, file_name in enumerate(audio_file_names)
]

if not args.disable_dry_run:
    logger.info("dry run, exiting...")
    sys.exit(0)

logger.debug("starting Flask server to receive transcript results...")
app = Flask(__name__)
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=23336, debug=True, use_reloader=False)).start()

pending_counter = 0


@app.route("/transcript_result/<int:index>", methods=["POST"])
def transcript_result_received(index):
    print(f"transcript result received for index {index}")
    transcript_file_path = transcript_file_paths[index]
    print(f"writing transcript to {transcript_file_path}...")
    with open(transcript_file_path, 'w') as f:
        f.write(request.get_data().decode('utf-8'))
    pending_counter -= 1
    logger.info(f"transcript {index} wrote to file ! still {pending_counter} transcripts pending")
    return "ok"


for index, request_params in enumerate(requests_params):
    logger.info(f"enqueuing transcript {index} for file {audio_file_names[index]}")
    logger.debug(f"request_params: {request_params}")
    logger.debug(f"headers: {headers}")
    response = requests.request(
        "POST",
        "https://api.spectropic.ai/v1/transcribe",
        json=requests_params[index],
        headers=headers
    )
    if response.status_code != 200:
        logger.error(f"response status code: {response.status_code}")
        logger.error(f"failed to enqueue transcript {index} for file {audio_file_names[index]}")
        continue
    pending_counter += 1

if pending_counter == 0:
    logger.info("no transcripts enqueued, exiting...")
    sys.exit(0)

logger.info(f"{pending_counter} transcripts enqueued, leave this running until the responses are received !")
