# Piper it_IT-riccardo-x_low con misura dei tempi.
import os, subprocess, time, json
import soundfile as sf
T = os.environ["TESTO"]
nome = "piper-it_IT-riccardo-x_low"
t0 = time.time()
subprocess.run(["piper", "-m", "r.onnx", "-f", f"out/{nome}.wav"], input=T.encode("utf-8"), check=True)
s = time.time() - t0
d = sf.info(f"out/{nome}.wav").duration
t = [{"file": nome, "durata_audio_s": round(d, 1), "tempo_cpu_s": round(s, 1), "rapporto": round(s / d, 2)}]
print(t)
json.dump(t, open("out/tempi-piper.json", "w"), indent=1)
