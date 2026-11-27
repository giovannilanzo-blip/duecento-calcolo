# Ritocco delle prove di sigla con la funzione repaint di ACE-Step 1.5: si rigenerano solo i tratti indicati.
# Uso: python ritocca.py <cartella ACE-Step> <lavoro: A2 oppure C2> <wav di partenza> <seme> <cartella di uscita>
import json, os, sys, time, shutil

ACE, LAV, SRC, SEED, OUT = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), int(sys.argv[4]), os.path.abspath(sys.argv[5])
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ACE)
os.chdir(ACE)

STRUMENTI = ("tabor and frame drums, shawm and bombarde, wooden recorder and wooden transverse flute, "
             "medieval vielle fiddle, hurdy-gurdy drone, lute, psaltery, church bells")
BASE = {
    "A": ("Solemn processional medieval instrumental, 13th-century Italian early music ensemble, acoustic, historically "
          f"informed: {STRUMENTI}."),
    "C": (f"Epic medieval instrumental played only on authentic 13th-century acoustic instruments: {STRUMENTI}. "
          "Early music ensemble, heroic and dramatic."),
}
STRUTTURA = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "struttura.txt"), encoding="utf-8").read()
# tratti da rigenerare: (inizio, fine, descrizione del tratto, forza del repaint 0-1)
LAVORI = {
    "A2": ("A", [
        (50.0, 64.0, "Climax: battle charge, fortissimo, the full ensemble at maximum power, thundering tabor and frame drums "
                     "on every beat, loud shawms and bombardes, dense and powerful, a huge drum impact on the downbeat.", 0.85),
        (86.0, 100.0, "Grand triumphant climax: main theme fortissimo, full ensemble with ringing church bells, loud shawms, "
                      "pounding frame drums, a massive impact on the first downbeat, majestic and dense.", 0.85),
    ]),
    "C2": ("C", [
        (76.0, 90.0, "Peaceful but full and continuous: steady lute, recorder and hurdy-gurdy drone with soft frame drum, "
                     "no pause, no silence, gradual crescendo in the last bars leading into a powerful climax.", 0.85),
        (106.0, 120.0, "Final cadence of the full ensemble, music continues to the very end, closing on one last loud tabor "
                       "stroke followed by ringing resonance and bells decaying.", 0.9),
    ]),
}
var, tratti = LAVORI[LAV]
info = {"lavoro": LAV, "partenza": os.path.basename(SRC), "seme": SEED, "tratti": [], "bpm": 120}
t0 = time.time()
from acestep.handler import AceStepHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

dit = AceStepHandler()
msg, ok = dit.initialize_service(project_root=ACE, config_path="acestep-v15-turbo", device="cpu", offload_to_cpu=False)
print("DiT:", ok, msg, flush=True)
if not ok:
    sys.exit(1)
cur = SRC
for k, (a, b, desc, forza) in enumerate(tratti):
    t1 = time.time()
    params = GenerationParams(task_type="repaint", src_audio=cur, repainting_start=a, repainting_end=b,
                              chunk_mask_mode="explicit", repaint_mode="balanced", repaint_strength=forza,
                              caption=BASE[var] + " " + desc, lyrics=STRUTTURA, instrumental=True, vocal_language="unknown",
                              bpm=120, keyscale="D minor", timesignature="4", duration=120.0, inference_steps=8,
                              guidance_scale=1.0, seed=SEED + k, thinking=False, use_cot_metas=False,
                              use_cot_caption=False, use_cot_language=False)
    config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[SEED + k], audio_format="wav")
    res = generate_music(dit, None, params=params, config=config, save_dir=os.path.join(OUT, f"grezzi{k}"))
    print("tratto", a, b, "esito:", res.success, res.status_message, flush=True)
    if not res.success or not res.audios or not res.audios[0].get("path"):
        sys.exit(2)
    cur = res.audios[0]["path"]
    info["tratti"].append({"da_s": a, "a_s": b, "descrizione": desc, "forza": forza, "secondi": round(time.time() - t1, 1)})
shutil.copy(cur, os.path.join(OUT, f"sigla-{LAV}-s{SEED}.wav"))
info["totale_s"] = round(time.time() - t0, 1)
json.dump(info, open(os.path.join(OUT, f"sigla-{LAV}-s{SEED}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(info, ensure_ascii=False, indent=1))
