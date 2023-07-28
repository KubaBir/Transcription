import whisper

model = whisper.load_model("small")
audio = whisper.load_audio('output.wav')
audio = whisper.pad_or_trim(audio)

mel = whisper.log_mel_spectrogram(audio).to(model.device)
options = whisper.DecodingOptions(fp16=False)

original = whisper.decode(model, mel, options).text
print(original)
