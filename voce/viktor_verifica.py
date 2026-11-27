# Controllo delle letture con Whisper: trascrive ogni mp3 e lo confronta con il testo preparato per la sintesi.
# Una somiglianza bassa segnala parole saltate, ripetute o storpiate, da ascoltare con attenzione.
# Uso: python voce/viktor_verifica.py ELENCO.json CARTELLA_MP3 [MODELLO]
import glob, json, os, re, sys, difflib
from faster_whisper import WhisperModel
elenco, cartella = sys.argv[1], sys.argv[2]
modello = sys.argv[3] if len(sys.argv) > 3 else "small"
testi = {x["chiave"]: x for x in json.load(open(elenco, encoding="utf8"))}
m = WhisperModel(modello, device="cpu", compute_type="int8")
def parole(t): return re.sub(r"[^a-zàèéìòù' ]", " ", t.lower().replace("’", "'")).split()
righe = []
for f in sorted(glob.glob(os.path.join(cartella, "**", "*.mp3"), recursive=True)):
    k = os.path.basename(f)[:-4]
    if k not in testi: continue
    seg, _ = m.transcribe(f, language="it", beam_size=5)
    t = " ".join(s.text.strip() for s in seg)
    r = difflib.SequenceMatcher(None, parole(testi[k]["lettura"]), parole(t)).ratio()
    righe.append((r, k, t)); print(f"{r:.2f} {k} {t}", flush=True)
righe.sort()
with open(os.path.join(cartella, "verifica.txt"), "w", encoding="utf8") as out:
    for r, k, t in righe:
        print(f"{r:.2f} | {k} | atteso: {testi[k]['lettura']}\n     | trascritto: {t}", file=out)
