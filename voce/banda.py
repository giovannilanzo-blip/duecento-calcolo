# Analisi della banda e del fruscio: legge ogni file con ffmpeg alla frequenza nativa e misura lo spettro medio del parlato.
import glob, json, subprocess, sys
import numpy as np

def leggi(p):
    sr = int(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=sample_rate",
                             "-of", "csv=p=0", p], capture_output=True, text=True).stdout.strip())
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "1", "-f", "f32le", "-"], capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32), sr

def analizza(p):
    x, sr = leggi(p)
    n, hop = 2048, 512
    w = np.hanning(n)
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::hop] * w
    S = np.abs(np.fft.rfft(fr, axis=1)) ** 2
    f = np.fft.rfftfreq(n, 1 / sr)
    e = 10 * np.log10(S.sum(1) + 1e-20)
    parlato = e > e.max() - 35
    spe = 10 * np.log10(S[parlato].mean(0) + 1e-20)
    k = max(1, int(150 / (sr / n)))
    spe = np.convolve(spe, np.ones(k) / k, mode="same")
    spe -= spe.max()
    sopra = np.where(spe > -60)[0]
    banda60 = float(f[sopra.max()]) if len(sopra) else 0.0
    sopra50 = np.where(spe > -50)[0]
    banda50 = float(f[sopra50.max()]) if len(sopra50) else 0.0
    tot = S[parlato].sum()
    quota4k = float(S[parlato][:, f >= 4000].sum() / tot * 100)
    quota8k = float(S[parlato][:, f >= 8000].sum() / tot * 100)
    # Fruscio: energia sopra i 3 kHz nelle pause (10% dei frame meno energici), in dBFS.
    hf = 10 * np.log10(S[:, f >= 3000].sum(1) / (w ** 2).sum() + 1e-20)
    pausa = e < e.max() - 45
    fruscio = float(np.median(hf[pausa])) if pausa.sum() >= 5 else float("nan")
    # Piattezza spettrale fra 5 e 11 kHz durante il parlato: vicina a 1 per il fruscio, bassa per armoniche e consonanti.
    b = (f >= 5000) & (f <= 11000)
    Sb = S[parlato][:, b] + 1e-20
    piatt = float(np.median(np.exp(np.log(Sb).mean(1)) / Sb.mean(1)))
    return {"file": p, "sr": sr, "banda_-50dB_Hz": round(banda50), "banda_-60dB_Hz": round(banda60),
            "energia_sopra_4k_%": round(quota4k, 2), "energia_sopra_8k_%": round(quota8k, 3),
            "fruscio_pause_dBFS": round(max(fruscio, -140), 1) if fruscio == fruscio else None,
            "piattezza_5_11k": round(piatt, 3)}

if __name__ == "__main__":
    ris = []
    for p in sys.argv[2:] if len(sys.argv) > 2 else sorted(glob.glob(f"{sys.argv[1]}/**/*.wav", recursive=True)):
        try:
            ris.append(analizza(p)); print(ris[-1], flush=True)
        except Exception as ex:
            print(p, "errore", ex, flush=True)
    json.dump(ris, open(f"{sys.argv[1]}/banda.json", "w"), indent=1)
