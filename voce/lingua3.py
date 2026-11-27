# Controllo dell'accento con Whisper: trascrizione in italiano e probabilità della lingua riconosciuta senza indicazione.
import glob, json, os, sys
from faster_whisper import WhisperModel
cartella = sys.argv[1]
m = WhisperModel(os.environ.get("WHISPER", "medium"), device="cpu", compute_type="int8")
ris = []
for f in sorted(glob.glob(f"{cartella}/**/*.wav", recursive=True)):
    seg, _ = m.transcribe(f, language="it", beam_size=5)
    seg = list(seg)
    t = " ".join(s.text.strip() for s in seg)
    logp = sum(s.avg_logprob for s in seg) / max(1, len(seg))
    _, info = m.transcribe(f, beam_size=1)
    probs = sorted(info.all_language_probs or [], key=lambda x: -x[1])[:3]
    ris.append({"file": os.path.basename(f), "testo": t, "logprob_medio": round(logp, 3),
                "lingua": info.language, "prob_lingua": round(info.language_probability, 3),
                "prime_lingue": [[l, round(p, 3)] for l, p in probs]})
    print(ris[-1], flush=True)
json.dump(ris, open(f"{cartella}/lingua.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
