# Voce italiana con Chatterbox multilingue, voce predefinita del modello (nessuna clonazione).
import json, os, sys, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
frasi = json.loads(os.environ["FRASI"]); uscita = sys.argv[1]; os.makedirs(uscita, exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
for i, f in enumerate(frasi, 1):
    wav = m.generate(f, language_id="it")
    torchaudio.save(os.path.join(uscita, f"chatterbox-frase{i}.wav"), wav, m.sr)
    print("scritta", i, flush=True)
