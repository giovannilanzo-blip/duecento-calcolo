# Analisi delle prove di sigla: tempo, colpi, intensita' per scena e riconoscimento degli strumenti con CLAP.
import sys, json, glob, os
import numpy as np, librosa

SCENE = [(1, 0, 8), (2, 8, 18), (3, 18, 32), (4, 32, 42), (5, 42, 52), (6, 52, 62), (7, 62, 72), (8, 72, 88),
         (9, 88, 98), (10, 98, 112), (11, 112, 120)]
INTENSITA = {1: 3, 2: 2, 3: 3, 4: 3, 5: 4, 6: 5, 7: 2, 8: 2, 9: 5, 10: 4, 11: 3}
COLPI = [6.0, 58.0, 88.0, 118.0]
ANTICHI = ["hurdy-gurdy", "recorder flute", "wooden transverse flute", "shawm", "bagpipe", "medieval fiddle",
           "lute", "psaltery dulcimer", "frame drum", "tabor drum", "church bells", "harp"]
MODERNI = ["drum kit", "electric guitar", "synthesizer", "orchestral violin section", "epic choir", "piano",
           "electric bass", "brass section trumpets"]

clap = None
try:
    import torch
    from transformers import ClapModel, ClapProcessor
    clap = (ClapModel.from_pretrained("laion/larger_clap_music"), ClapProcessor.from_pretrained("laion/larger_clap_music"))
except Exception as e:
    print("CLAP non disponibile:", e)

rap = {}
for f in sorted(glob.glob(os.path.join(sys.argv[1], "sigla-*.wav"))):
    y, sr = librosa.load(f, sr=22050, mono=True)
    d = {"durata_s": round(len(y) / sr, 2)}
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr, start_bpm=120)
    d["bpm_stimato"] = round(float(np.atleast_1d(tempo)[0]), 1)
    bt = librosa.frames_to_time(beats, sr=sr)
    # scarto medio dei battiti dalla griglia da 0,5 s
    if len(bt):
        sc = (bt - np.round(bt / 0.5) * 0.5)
        d["scarto_medio_griglia_s"] = round(float(np.mean(np.abs(sc))), 3)
        d["fase_media_s"] = round(float(np.median(sc)), 3)
    on = librosa.onset.onset_strength(y=y, sr=sr)
    ot = librosa.times_like(on, sr=sr)
    med = float(np.median(on)) + 1e-9
    d["colpi"] = {}
    for c in COLPI:
        m = (ot > c - 0.25) & (ot < c + 0.25)
        if m.any():
            i = np.argmax(on[m]); d["colpi"][str(c)] = {"forza_rel": round(float(on[m][i] / med), 1), "istante": round(float(ot[m][i]), 2)}
    rms = librosa.feature.rms(y=y)[0]; rt = librosa.times_like(rms, sr=sr)
    db = 20 * np.log10(rms + 1e-6)
    d["livello_scene_db"] = {str(n): round(float(np.mean(db[(rt >= a) & (rt < b)])), 1) for n, a, b in SCENE if ((rt >= a) & (rt < b)).any()}
    d["intensita_mappa"] = INTENSITA
    if clap is not None:
        model, proc = clap
        etichette = [f"the sound of {x}" for x in ANTICHI + MODERNI]
        with torch.no_grad():
            ti = proc.tokenizer(etichette, return_tensors="pt", padding=True)
            te = model.get_text_features(**ti); te = te / te.norm(dim=-1, keepdim=True)
        y48, _ = librosa.load(f, sr=48000, mono=True)
        fin = []
        for a in range(0, int(len(y48) / 48000) - 4, 10):
            seg = y48[a * 48000:(a + 10) * 48000]
            ai = proc.feature_extractor(seg, sampling_rate=48000, return_tensors="pt")
            with torch.no_grad():
                ae = model.get_audio_features(**ai); ae = ae / ae.norm(dim=-1, keepdim=True)
                p = (100.0 * ae @ te.T).softmax(-1)[0].numpy()
            top = np.argsort(-p)[:4]
            mod = sum(float(p[len(ANTICHI) + k]) for k in range(len(MODERNI)))
            fin.append({"da_s": a, "top": [(ANTICHI + MODERNI)[k] + f" {p[k]:.2f}" for k in top], "quota_moderni": round(mod, 2)})
        d["clap_finestre_10s"] = fin
        d["clap_quota_moderni_media"] = round(float(np.mean([x["quota_moderni"] for x in fin])), 2)
    rap[os.path.basename(f)] = d
    print(os.path.basename(f), json.dumps(d, ensure_ascii=False, indent=1), flush=True)
json.dump(rap, open(os.path.join(sys.argv[1], "analisi.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
