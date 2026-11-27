# MOSS-TTS-Nano: voci predefinite maschili e voce sintetica Kokoro come riferimento. Si esegue dalla cartella nano.
import os, subprocess, time, json
import soundfile as sf
T = os.environ["TESTO"]
tempi = []
prove = [("moss-nano-Adam", ["--voice", "Adam"]), ("moss-nano-Nathan", ["--voice", "Nathan"]),
         ("moss-nano-Junhao", ["--voice", "Junhao"]),
         ("moss-nano-rif_kokoro_nicola", ["--prompt-audio-path", "../kok/kokoro-im_nicola.wav"])]
for nome, a in prove:
    t0 = time.time()
    subprocess.run(["python", "infer_onnx.py", "--text", T, "--cpu-threads", "2",
                    "--output-audio-path", f"../out/{nome}.wav"] + a)
    s = time.time() - t0
    try:
        d = sf.info(f"../out/{nome}.wav").duration
        tempi.append({"file": nome, "durata_audio_s": round(d, 1), "tempo_cpu_s": round(s, 1), "rapporto": round(s / d, 2)})
    except Exception as e:
        tempi.append({"file": nome, "errore": str(e)})
    print(tempi[-1], flush=True)
json.dump(tempi, open("../out/tempi-moss.json", "w"), indent=1)
