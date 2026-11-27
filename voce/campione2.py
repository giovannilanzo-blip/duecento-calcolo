# Secondo campionario delle voci italiane, maschili e femminili: ogni motore legge la stessa frase e registra i tempi in CPU.
import os, sys, time, json
import numpy as np
import soundfile as sf
TESTO = os.environ["TESTO"]
RIF_TESTO = "Benvenuti nel Duecento. Oggi raccontiamo la storia delle città toscane, dei loro mercanti e dei loro eserciti."
motore, uscita = sys.argv[1], sys.argv[2]
os.makedirs(uscita, exist_ok=True)
tempi = []
def salva(nome, wav, sr, t0):
    wav = np.asarray(wav, dtype=np.float32).squeeze()
    sf.write(os.path.join(uscita, nome + ".wav"), wav, sr)
    dur = len(wav) / sr; sec = time.time() - t0
    tempi.append({"file": nome, "sr": sr, "durata_audio_s": round(dur, 1), "tempo_cpu_s": round(sec, 1),
                  "rapporto": round(sec / dur, 2), "caratteri": len(TESTO)})
    print(tempi[-1], flush=True)

# Descrizioni delle voci progettate (nessuna persona reale).
QWEN = {
    "M1-narratore_caldo": "A warm, deep male voice of a 45-year-old Italian native speaker. He is a storyteller narrating history to children, with a lively and engaging intonation, natural rises and falls, moderate pace. Clear studio recording, no background noise, standard Italian pronunciation without any foreign accent.",
    "M2-giovane_vivace": "A young, bright and energetic male voice, about 28 years old, Italian native speaker. He is an enthusiastic narrator for educational videos for kids, very expressive and dynamic, with a smiling tone. Clear studio recording, no background noise, standard Italian pronunciation without any foreign accent.",
    "M3-documentario": "A mature, resonant male voice, Italian native speaker, documentary narrator for a history program. Authoritative yet warm, measured pace, dramatic emphasis on key words. Clear studio recording, broadcast quality, no background noise, standard Italian pronunciation without any foreign accent.",
    "F1-narratrice_calda": "A warm, clear female voice, about 35 years old, Italian native speaker. She is a storyteller for children, gentle and engaging, with a lively intonation and moderate pace. Clear studio recording, no background noise, standard Italian pronunciation without any foreign accent.",
    "F2-insegnante_dolce": "An expressive and sweet female teacher voice, about 40 years old, Italian native speaker. She explains history to middle-school students with enthusiasm and kindness, with varied and vivid intonation. Clear studio recording, no background noise, standard Italian pronunciation without any foreign accent.",
    "F3-documentario": "A mature, elegant female voice, Italian native speaker, documentary narrator for a history program. Confident and expressive, measured pace, dramatic emphasis on key words. Clear studio recording, broadcast quality, no background noise, standard Italian pronunciation without any foreign accent.",
}

if motore.startswith("qwen-"):
    import torch
    from qwen_tts import Qwen3TTSModel
    torch.set_num_threads(os.cpu_count())
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.bfloat16)
    k = motore[5:]; d = QWEN[k]
    for seme in [1256, 1176]:
        torch.manual_seed(seme); t0 = time.time()
        wavs, sr = m.generate_voice_design(text=TESTO, language="Italian", instruct=d)
        salva(f"qwen3vd-{k}-s{seme}", wavs[0], sr, t0)
    if k in ("M1-narratore_caldo", "F1-narratrice_calda"):
        # Riferimento sintetico per i modelli che clonano una voce (F5-TTS, Chatterbox).
        torch.manual_seed(1256)
        wavs, sr = m.generate_voice_design(text=RIF_TESTO, language="Italian", instruct=d)
        sf.write(os.path.join(uscita, f"rif-{k[0]}.wav"), np.asarray(wavs[0], dtype=np.float32), sr)
        open(os.path.join(uscita, f"rif-{k[0]}.txt"), "w", encoding="utf-8").write(RIF_TESTO)

elif motore == "kokoro":
    from kokoro import KPipeline
    p = KPipeline(lang_code="i")
    for v in ["if_sara", "im_nicola"]:
        t0 = time.time()
        wav = np.concatenate([a.numpy() if hasattr(a, "numpy") else a for _, _, a in p(TESTO, voice=v, speed=0.95)])
        salva(f"kokoro-{v}", wav, 24000, t0)

elif motore == "orpheus":
    # Orpheus 3B italiano/spagnolo di Canopy Labs, quantizzato Q8_0 (GGUF), con decodificatore SNAC a 24 kHz.
    import re, torch
    from llama_cpp import Llama
    from snac import SNAC
    llm = Llama(model_path="orpheus.gguf", n_ctx=4096, n_threads=os.cpu_count(), verbose=False, seed=1256)
    snac = SNAC.from_pretrained("hubertsiuzdak/snac_24khz").eval()
    frasi = [f.strip() for f in re.split(r"(?<=[.!?])\s+", TESTO) if f.strip()]
    def decodifica(codici):
        n = len(codici) // 7
        c = codici[: n * 7]
        l1, l2, l3 = [], [], []
        for i in range(n):
            g = c[7 * i: 7 * i + 7]
            l1.append(g[0]); l2.append(g[1] - 4096); l3.append(g[2] - 2 * 4096); l3.append(g[3] - 3 * 4096)
            l2.append(g[4] - 4 * 4096); l3.append(g[5] - 5 * 4096); l3.append(g[6] - 6 * 4096)
        cod = [torch.tensor(x).unsqueeze(0) for x in (l1, l2, l3)]
        if any((t < 0).any() or (t > 4095).any() for t in cod):
            print("codici fuori intervallo, si tagliano", flush=True)
            cod = [t.clamp(0, 4095) for t in cod]
        with torch.inference_mode():
            return snac.decode(cod).squeeze().numpy()
    for voce in ["pietro", "carlo", "giulia"]:
        t0 = time.time(); pezzi = []
        for f in frasi:
            ids = [128259] + llm.tokenize(f"{voce}: {f}".encode("utf-8"), add_bos=True, special=False) + [128009, 128260]
            llm.reset(); out = []
            for tok in llm.generate(ids, temp=0.6, top_p=0.9, top_k=40, repeat_penalty=1.1, reset=True):
                if tok == 128258 or len(out) > 2400:
                    break
                out.append(tok)
            if 128257 in out:
                out = out[len(out) - out[::-1].index(128257):]
            codici = [t - 128266 for t in out if t >= 128266]
            print(voce, f[:30], "token", len(out), "codici", len(codici), flush=True)
            pezzi.append(decodifica(codici)); pezzi.append(np.zeros(int(0.3 * 24000), dtype=np.float32))
        salva(f"orpheus-{voce}", np.concatenate(pezzi[:-1]), 24000, t0)

json.dump(tempi, open(os.path.join(uscita, f"tempi-{motore}.json"), "w"), indent=1)
