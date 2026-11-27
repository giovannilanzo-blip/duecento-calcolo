# Chatterbox multilingue con la voce sintetica Kokoro im_nicola come riferimento (nessuna persona reale).
import os, sys, time, json, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
TESTO = os.environ["TESTO"]
rif, uscita = sys.argv[1], sys.argv[2]
os.makedirs(uscita, exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
tempi = []
for nome, kw in [("chatterbox-rif_kokoro_nicola", dict(audio_prompt_path=rif, exaggeration=0.5, cfg_weight=0.5))]:
    t0 = time.time()
    wav = m.generate(TESTO, language_id="it", **kw)
    torchaudio.save(os.path.join(uscita, nome + ".wav"), wav, m.sr)
    d = wav.shape[-1] / m.sr
    s = time.time() - t0
    tempi.append({"file": nome, "durata_audio_s": round(d, 1), "tempo_cpu_s": round(s, 1), "rapporto": round(s / d, 2)})
    print(tempi[-1], flush=True)
json.dump(tempi, open(os.path.join(uscita, "tempi-chatterbox.json"), "w"), indent=1)
