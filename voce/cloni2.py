# Chatterbox multilingue con le voci sintetiche Qwen3 VoiceDesign come riferimento (nessuna persona reale).
import os, sys, time, json, torchaudio
from chatterbox.mtl_tts import ChatterboxMultilingualTTS
TESTO = os.environ["TESTO"]
cartella_rif, uscita = sys.argv[1], sys.argv[2]
os.makedirs(uscita, exist_ok=True)
m = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
tempi = []
for s in ["M", "F"]:
    nome = f"chatterbox-rif_qwen3vd_{s}"
    t0 = time.time()
    wav = m.generate(TESTO, language_id="it", audio_prompt_path=f"{cartella_rif}/rif-{s}.wav", exaggeration=0.6, cfg_weight=0.5)
    torchaudio.save(os.path.join(uscita, nome + ".wav"), wav, m.sr)
    d = wav.shape[-1] / m.sr; sec = time.time() - t0
    tempi.append({"file": nome, "sr": m.sr, "durata_audio_s": round(d, 1), "tempo_cpu_s": round(sec, 1), "rapporto": round(sec / d, 2), "caratteri": len(TESTO)})
    print(tempi[-1], flush=True)
json.dump(tempi, open(os.path.join(uscita, "tempi-chatterbox.json"), "w"), indent=1)
