# Letture del narratore con Kokoro-82M, voce «im_nicola» (italiano, maschile, licenza Apache 2.0).
# Ogni testo arriva già preparato in voce/viktor/*.json (campo «lettura»: numeri e date in lettere, nomi stranieri
# riscritti, virgolette e parentesi trasformate in pause). Con Kokoro la punteggiatura resta quella del testo preparato.
# Kokoro divide il testo alle frasi (split_pattern); i pezzi si uniscono con una breve pausa, poi ffmpeg normalizza
# il volume a -21 LUFS e salva un mp3 a 64 kbps mono, 44,1 kHz, con il nome <chiave>.mp3, la stessa chiave che il
# gioco calcola con GG.voceChiave(testo). Nessun filtro di ammorbidimento.
# Uso: python voce/nicola.py ELENCO.json USCITA PARTE PARTI [SCADENZA_SECONDI] [FATTI.txt]
import os, sys, json, time, subprocess, gc
import numpy as np
import soundfile as sf
import torch
from kokoro import KPipeline

elenco, uscita = sys.argv[1], sys.argv[2]
parte, parti = int(sys.argv[3]), int(sys.argv[4])
scadenza = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9
fatti = set()
if len(sys.argv) > 6 and os.path.exists(sys.argv[6]):
    fatti = set(x.strip() for x in open(sys.argv[6], encoding="utf8") if x.strip())
VOCE, SR = os.environ.get("VOCE", "im_nicola"), 24000   # anche una voce femminile italiana di Kokoro, per esempio if_sara
VELOCITA = float(os.environ.get("VELOCITA", "0.95"))   # la stessa velocità del campione ascoltato da Giovanni
PAUSA, BORDO = 0.25, 0.12
t_avvio = time.time()

testi = json.load(open(elenco, encoding="utf8"))
carichi = [0] * parti; mio = []
for i in sorted(range(len(testi)), key=lambda i: (-len(testi[i]["lettura"]), testi[i]["chiave"])):
    p = min(range(parti), key=lambda j: (carichi[j], j))
    carichi[p] += len(testi[i]["lettura"])
    if p == parte - 1: mio.append(testi[i])
mio = [x for x in mio if x["chiave"] not in fatti]
print(f"lotto {parte}/{parti}: {len(mio)} testi, {sum(len(x['lettura']) for x in mio)} caratteri", flush=True)

torch.set_num_threads(os.cpu_count() or 2)
pipe = KPipeline(lang_code="i")
os.makedirs(uscita, exist_ok=True)
registro, mancanti = [], []

for n, x in enumerate(mio):
    if time.time() - t_avvio > scadenza:
        mancanti.append(x["chiave"]); continue
    t0 = time.time(); pezzi = [np.zeros(int(BORDO * SR), np.float32)]; fon = []
    with torch.inference_mode():
        for _, ps, a in pipe(x["lettura"], voice=VOCE, speed=VELOCITA, split_pattern=r"(?<=[.!?;:])\s+"):
            fon.append(str(ps))
            if a is None: continue
            a = a.numpy() if hasattr(a, "numpy") else np.asarray(a)
            pezzi += [a.astype(np.float32), np.zeros(int(PAUSA * SR), np.float32)]
    pezzi[-1] = np.zeros(int(BORDO * SR), np.float32)
    wav = np.concatenate(pezzi)
    tmp = os.path.join(uscita, x["chiave"] + ".wav"); sf.write(tmp, wav, SR)
    mp3 = os.path.join(uscita, x["chiave"] + ".mp3")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-21:TP=-2:LRA=11",
                    "-ar", "44100", "-ac", "1", "-b:a", "64k", mp3], check=True)
    os.remove(tmp)
    if os.environ.get("FONEMI"):   # fonemi di Kokoro con gli accenti tonici (ˈ), per controllare la pronuncia
        open(os.path.join(uscita, x["chiave"] + ".fonemi.txt"), "w", encoding="utf8").write(x["lettura"] + "\n" + " | ".join(fon) + "\n")
    dur = len(wav) / SR; sec = time.time() - t0
    del wav, pezzi; gc.collect()
    registro.append({"chiave": x["chiave"], "gruppo": x["gruppo"], "durata_s": round(dur, 1), "calcolo_s": round(sec, 1)})
    print(f"{n + 1}/{len(mio)} {x['chiave']} {dur:.1f} s audio, {sec:.1f} s calcolo", flush=True)

json.dump({"lotto": parte, "parti": parti, "fatti": registro, "mancanti": mancanti}, open(os.path.join(uscita, f"registro-{parte:02d}.json"), "w"), indent=1)
tot_a = sum(r["durata_s"] for r in registro); tot_c = sum(r["calcolo_s"] for r in registro)
print(f"FINE lotto {parte}: {len(registro)} fatti, {len(mancanti)} mancanti, audio {tot_a / 60:.1f} min, calcolo {tot_c / 60:.1f} min, rapporto {tot_c / max(tot_a, 1):.2f}", flush=True)
