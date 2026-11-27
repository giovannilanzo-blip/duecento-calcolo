# Trascrizione di controllo con Whisper small: misura quanto la pronuncia italiana resta comprensibile.
import glob, sys
from faster_whisper import WhisperModel
cartella = sys.argv[1]
m = WhisperModel("small", device="cpu", compute_type="int8")
with open(f"{cartella}/trascrizioni.txt", "w", encoding="utf-8") as out:
    for f in sorted(glob.glob(f"{cartella}/**/*.wav", recursive=True)):
        seg, _ = m.transcribe(f, language="it", beam_size=5)
        t = " ".join(s.text.strip() for s in seg)
        print(f, "=>", t, flush=True)
        print(f, "|", t, file=out)
