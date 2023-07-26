from TTS.api import TTS

# List available 🐸TTS models and choose the first one
print(TTS.list_models())
model_name = TTS.list_models()[1]
# Init TTS
tts = TTS(model_name="tts_models/en/blizzard2013/capacitron-t2-c150_v2",
          progress_bar=True)

tts.tts_to_file(text="My name is Jack", file_path="output.wav")
