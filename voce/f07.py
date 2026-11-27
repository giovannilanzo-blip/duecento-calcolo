# Letture della narratrice con Chatterbox multilingue (licenza MIT), voce «F07» del campionario 3:
# clone della voce sintetica Qwen3 VoiceDesign «narratrice calda» (voce/rif/rif-F.wav, nessuna persona reale),
# con exaggeration 0,6 e cfg_weight 0,5 come nel campionario.
# Il testo preparato (campo «lettura») si divide alle frasi; ogni frase si sintetizza da sola, con la sua punteggiatura,
# e le frasi si uniscono con una breve pausa. ffmpeg normalizza il volume a -21 LUFS e salva un mp3 a 64 kbps mono,
# 44,1 kHz, con il nome <chiave>.mp3 (la chiave GG.voceChiave del gioco).
# Uso: python voce/f07.py ELENCO.json USCITA PARTE PARTI [SCADENZA_SECONDI] [FATTI.txt]
import os, re, sys, json, time, subprocess, gc
import numpy as np
import soundfile as sf
import torch
from chatterbox.mtl_tts import ChatterboxMultilingualTTS

elenco, uscita = sys.argv[1], sys.argv[2]
parte, parti = int(sys.argv[3]), int(sys.argv[4])
scadenza = float(sys.argv[5]) if len(sys.argv) > 5 else 1e9
fatti = set()
if len(sys.argv) > 6 and os.path.exists(sys.argv[6]):
    fatti = set(x.strip() for x in open(sys.argv[6], encoding="utf8") if x.strip())
RIF = os.environ.get("RIF", "voce/rif/rif-F.wav")
ESAGERAZIONE, CFG = float(os.environ.get("ESAGERAZIONE", "0.6")), float(os.environ.get("CFG", "0.5"))
PAUSA, BORDO, MAXF = 0.25, 0.12, 250
t_avvio = time.time()

testi = json.load(open(elenco, encoding="utf8"))
carichi = [0] * parti; mio = []
for i in sorted(range(len(testi)), key=lambda i: (-len(testi[i]["lettura"]), testi[i]["chiave"])):
    p = min(range(parti), key=lambda j: (carichi[j], j))
    carichi[p] += len(testi[i]["lettura"])
    if p == parte - 1: mio.append(testi[i])
mio = [x for x in mio if x["chiave"] not in fatti]
print(f"lotto {parte}/{parti}: {len(mio)} testi, {sum(len(x['lettura']) for x in mio)} caratteri", flush=True)

def frasi(t):
    out = []
    for f in re.split(r"(?<=[.!?;:])\s+", t.strip()):
        while len(f) > MAXF:
            i = f.rfind(", ", 0, MAXF)
            if i < 40: break
            out.append(f[:i + 1]); f = f[i + 2:]
        if f: out.append(f)
    return out

torch.set_num_threads(os.cpu_count() or 2)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
SR = m.sr
os.makedirs(uscita, exist_ok=True)
registro, mancanti = [], []
for n, x in enumerate(mio):
    if time.time() - t_avvio > scadenza:
        mancanti.append(x["chiave"]); continue
    t0 = time.time(); pezzi = [np.zeros(int(BORDO * SR), np.float32)]
    for k, f in enumerate(frasi(x["lettura"])):
        torch.manual_seed(1256 + k)
        with torch.inference_mode():
            w = m.generate(f, language_id="it", audio_prompt_path=RIF, exaggeration=ESAGERAZIONE, cfg_weight=CFG)
        pezzi += [w.squeeze().cpu().numpy().astype(np.float32), np.zeros(int(PAUSA * SR), np.float32)]
    pezzi[-1] = np.zeros(int(BORDO * SR), np.float32)
    wav = np.concatenate(pezzi)
    tmp = os.path.join(uscita, x["chiave"] + ".wav"); sf.write(tmp, wav, SR)
    mp3 = os.path.join(uscita, x["chiave"] + ".mp3")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", tmp, "-af", "loudnorm=I=-21:TP=-2:LRA=11",
                    "-ar", "44100", "-ac", "1", "-b:a", "64k", mp3], check=True)
    os.remove(tmp)
    dur = len(wav) / SR; sec = time.time() - t0
    del wav, pezzi; gc.collect()
    registro.append({"chiave": x["chiave"], "gruppo": x["gruppo"], "durata_s": round(dur, 1), "calcolo_s": round(sec, 1)})
    print(f"{n + 1}/{len(mio)} {x['chiave']} {dur:.1f} s audio, {sec:.1f} s calcolo", flush=True)

json.dump({"lotto": parte, "parti": parti, "fatti": registro, "mancanti": mancanti}, open(os.path.join(uscita, f"registro-{parte:02d}.json"), "w"), indent=1)
tot_a = sum(r["durata_s"] for r in registro); tot_c = sum(r["calcolo_s"] for r in registro)
print(f"FINE lotto {parte}: {len(registro)} fatti, {len(mancanti)} mancanti, audio {tot_a / 60:.1f} min, calcolo {tot_c / 60:.1f} min, rapporto {tot_c / max(tot_a, 1):.2f}", flush=True)
