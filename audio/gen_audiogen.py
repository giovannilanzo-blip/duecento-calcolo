# Generazione dei rumori con AudioGen (audiocraft) in CPU, a piccoli gruppi salvati subito.
import json, os, sys, time
import torch, soundfile as sf
from audiocraft.models import AudioGen
lista, durata, parte, parti, uscita = sys.argv[1], float(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
gruppo = int(os.environ.get("GRUPPO", "3")); limite = float(os.environ.get("LIMITE_MIN", "44")) * 60
torch.set_num_threads(os.cpu_count() or 2)
lavori = json.load(open(lista, encoding="utf-8"))[parte::parti]
os.makedirs(uscita, exist_ok=True)
inizio = time.time()
m = AudioGen.get_pretrained("facebook/audiogen-medium", device="cpu")
m.set_generation_params(duration=durata, top_k=250, cfg_coef=3.0)
for i in range(0, len(lavori), gruppo):
    if time.time() - inizio > limite:
        print("tempo esaurito, si salta il resto", flush=True); break
    blocco = lavori[i:i + gruppo]; t = time.time()
    with torch.no_grad():
        wav = m.generate([p for _, p, _ in blocco], progress=True)
    for (nome, _, _), w in zip(blocco, wav):
        sf.write(os.path.join(uscita, nome + ".wav"), w.cpu().numpy().T, m.sample_rate)
        print("scritto", nome, round(time.time() - t), flush=True)
