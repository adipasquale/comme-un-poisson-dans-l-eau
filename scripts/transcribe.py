import whisper

model = whisper.load_model("medium")
result = model.transcribe("audio/1-specisme-appelons-un-chat-un-chat-valery-giroux-1-2.webm", language="fr", verbose=True)
print(result["text"])
