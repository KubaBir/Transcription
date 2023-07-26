from TTS.api import TTS
import tempfile
import os


print(*TTS.list_models(), sep='\n')

# Init TTS
tts = TTS(model_name="tts_models/es/mai/tacotron2-DDC")
print(tts.speakers)
print(tts.languages)
tts.tts_to_file("Ahora me he convertido en muerte, el destructor de mundos.",
                file_path="output.wav")

# with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
#     tts = TTS(model_name="tts_models/pl/mai_female/vits")
#     tts.tts_to_file(text="W chwili, kiedy zastanawiasz się czy kogoś kochasz, przestałeś go już kochać na zawsze.",
#                     file_path='output.wav')
# print(f.name)
# os.system("afplay " + f.name)
