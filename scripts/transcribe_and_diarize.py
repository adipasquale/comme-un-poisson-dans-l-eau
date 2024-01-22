import os
from whisperplus import (
    ASRDiarizationPipeline,
    format_speech_to_dialogue,
)

pipeline = ASRDiarizationPipeline.from_pretrained(
    asr_model="openai/whisper-tiny",
    diarizer_model="pyannote/speaker-diarization-3.1",
    use_auth_token="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",
    chunk_length_s=30,
    device="mps",
)
audio_dir = "audio"
output_dir = "output"

for filename in os.listdir(audio_dir):
    if filename.endswith(".webm"):
        audio_path = os.path.join(audio_dir, filename)
        output_path = os.path.join(
            output_dir, os.path.splitext(filename)[0] + ".txt")
        output_text = pipeline(audio_path, num_speakers=2, min_speaker=1,
                               max_speaker=2, language="fr", verbose=True)
        dialogue = format_speech_to_dialogue(output_text)
        with open(output_path, "w") as file:
            file.write(dialogue)
        print("wrote to", output_path)
