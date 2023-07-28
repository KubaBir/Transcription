from TTS.api import TTS
import tempfile
import os


print(*TTS.list_models(), sep='\n')

# Init TTS
tts = TTS(model_name="tts_models/en/jenny/jenny")
# tts = TTS(model_name="tts_models/es/css10/vits")
# print(tts.speakers)
# print(tts.languages)
tts.tts_to_file("when you wonder if you love someone, you have stopped loving them forever.",
                file_path="output.wav")
# tts.tts_to_file("cuando te preguntas si amas a alguien, has dejado de amarlo para siempre.",
# file_path="output.wav")

# with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
#     tts = TTS(model_name="tts_models/pl/mai_female/vits")
#     tts.tts_to_file(text="W chwili, kiedy zastanawiasz się czy kogoś kochasz, przestałeś go już kochać na zawsze.",
#                     file_path='output.wav')
# print(f.name)
# os.system("afplay " + f.name)
