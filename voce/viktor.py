# Letture del narratore con Coqui XTTS v2, voce predefinita «Viktor Eka», in italiano.
# Ogni testo arriva già preparato (voce/viktor/*.json): numeri in lettere, nomi stranieri riscritti, frasi senza punto finale.
# Ogni frase si sintetizza da sola; se la durata risulta anomala (frase allungata o troncata) si rigenera con un altro seme.
# Le frasi si uniscono con brevi pause, poi ffmpeg normalizza il volume e salva un mp3 a 64 kbps mono, 44,1 kHz,
# con il nome <chiave>.mp3, la stessa chiave che il gioco calcola con GG.voceChiave(testo).
# Uso: python voce/viktor.py ELENCO.json USCITA PARTE PARTI [SCADENZA_SECONDI] [FATTI.txt]
# Variabili d'ambiente facoltative:
#   FINE      chiusura di ogni frase: nulla (nessun segno), virgola, punto (il silenzio segue comunque nella pausa)
#   TEMP, TOP_P, REP, SPEED   impostazioni di XTTS (temperature, top_p, repetition_penalty, speed)
#   FILTRO    catena di filtri ffmpeg per ammorbidire il timbro, applicata prima della normalizzazione del volume
import os, sys, json, time, subprocess, gc, resource
import numpy as np
import soundfile as sf
import torch
from TTS.api import TTS

elenco, uscita = sys.argv[1], sys.argv[2]
parte, parti = int(sys.argv[3]), int(sys.argv[4])
scadenza = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9
fatti = set()
if len(sys.argv) > 6 and os.path.exists(sys.argv[6]):
    fatti = set(x.strip() for x in open(sys.argv[6], encoding="utf8") if x.strip())
VOCE, SR = "Viktor Eka", 24000
PAUSA, BORDO = 0.35, 0.12           # secondi fra le frasi e all'inizio e alla fine
CAR_AL_SECONDO = 13.9               # velocità media di Viktor Eka misurata nel campionario
t_avvio = time.time()
FINE = os.environ.get("FINE", "nulla")
FILTRO = os.environ.get("FILTRO", "").strip()
KW = {}
for nome, var in (("temperature", "TEMP"), ("top_p", "TOP_P"), ("repetition_penalty", "REP"), ("speed", "SPEED")):
    if os.environ.get(var): KW[nome] = float(os.environ[var])
print("impostazioni:", FINE, KW, FILTRO or "nessun filtro", flush=True)
def chiusa(f):
    if f.endswith("?"): return f
    return f + ("," if FINE == "virgola" else "." if FINE == "punto" else "")

testi = json.load(open(elenco, encoding="utf8"))
# lotti bilanciati per caratteri: il testo più lungo va al lotto più leggero (assegnazione deterministica)
carichi = [0] * parti; mio = []
for i in sorted(range(len(testi)), key=lambda i: (-sum(len(f) for f in testi[i]["frasi"]), testi[i]["chiave"])):
    p = min(range(parti), key=lambda j: (carichi[j], j))
    carichi[p] += sum(len(f) for f in testi[i]["frasi"])
    if p == parte - 1: mio.append(testi[i])
mio = [x for x in mio if x["chiave"] not in fatti]
print(f"lotto {parte}/{parti}: {len(mio)} testi, {sum(len(f) for x in mio for f in x['frasi'])} caratteri", flush=True)

torch.set_num_threads(os.cpu_count() or 2)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
os.makedirs(uscita, exist_ok=True)
registro, mancanti = [], []

def frase_audio(f):
    attesa = len(f) / CAR_AL_SECONDO / KW.get("speed", 1.0)
    f = chiusa(f)
    migliore = None
    for tentativo in range(3):
        torch.manual_seed(1256 + tentativo * 97)
        with torch.inference_mode():
            w = np.asarray(tts.tts(text=f, speaker=VOCE, language="it", split_sentences=False, **KW), dtype=np.float32)
        dur = len(w) / SR
        scarto = abs(dur - attesa) / max(attesa, 0.8)
        if migliore is None or scarto < migliore[1]: migliore = (w, scarto, tentativo)
        if 0.45 * attesa - 0.6 <= dur <= 1.9 * attesa + 1.2: break
    return migliore

for n, x in enumerate(mio):
    if time.time() - t_avvio > scadenza:
        mancanti.append(x["chiave"]); continue
    t0 = time.time(); pezzi = [np.zeros(int(BORDO * SR), np.float32)]; tent = []
    for f in x["frasi"]:
        w, scarto, tentativo = frase_audio(f)
        tent.append(tentativo)
        pezzi += [w, np.zeros(int(PAUSA * SR), np.float32)]
    pezzi[-1] = np.zeros(int(BORDO * SR), np.float32)
    wav = np.concatenate(pezzi)
    tmp = os.path.join(uscita, x["chiave"] + ".wav"); sf.write(tmp, wav, SR)
    mp3 = os.path.join(uscita, x["chiave"] + ".mp3")
    af = (FILTRO + "," if FILTRO else "") + "loudnorm=I=-21:TP=-2:LRA=11"
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-af", af,
                    "-ar", "44100", "-ac", "1", "-b:a", "64k", mp3], check=True)
    os.remove(tmp)
    dur = len(wav) / SR; sec = time.time() - t0
    del wav, pezzi; gc.collect()
    registro.append({"chiave": x["chiave"], "gruppo": x["gruppo"], "durata_s": round(dur, 1), "calcolo_s": round(sec, 1),
                     "frasi": len(x["frasi"]), "rigenerate": sum(1 for t in tent if t > 0)})
    print(f"{n + 1}/{len(mio)} {x['chiave']} {dur:.1f} s audio, {sec:.1f} s calcolo, rigenerate {registro[-1]['rigenerate']}, memoria massima {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024} MB", flush=True)

json.dump({"lotto": parte, "parti": parti, "fatti": registro, "mancanti": mancanti}, open(os.path.join(uscita, f"registro-{parte:02d}.json"), "w"), indent=1)
tot_a = sum(r["durata_s"] for r in registro); tot_c = sum(r["calcolo_s"] for r in registro)
print(f"FINE lotto {parte}: {len(registro)} fatti, {len(mancanti)} mancanti, audio {tot_a / 60:.1f} min, calcolo {tot_c / 60:.1f} min, rapporto {tot_c / max(tot_a, 1):.2f}", flush=True)
