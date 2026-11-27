# Strati aggiuntivi per la sigla ricomposta: funzione «lego» di ACE-Step 1.5 (modello base), che genera una sola
# traccia strumentale a tempo con l'audio di contesto.
# Uso: python strati.py <cartella ACE-Step> <strato> <audio di contesto> <seme> <cartella di uscita>
import json, os, sys, time, shutil
ACE, STRATO, SRC, SEED, OUT = sys.argv[1], sys.argv[2], os.path.abspath(sys.argv[3]), int(sys.argv[4]), os.path.abspath(sys.argv[5])
os.makedirs(OUT, exist_ok=True); sys.path.insert(0, ACE); os.chdir(ACE)
STRATI = {
    "tamburi": ("percussion", "Medieval percussion only: deep tabor drum and large frame drums played by hand, steady marching "
                "rhythm locked to the beat, strong accents on the downbeats, acoustic, 13th-century early music."),
    "fiati": ("woodwinds", "Medieval double reeds only: shawms and bombardes doubling the main melody, loud and festive, "
              "with wooden recorder lines, acoustic 13th-century early music ensemble."),
    "campane": ("percussion", "Church bells and small handbells only, ringing on the downbeats, medieval Italian bell tower, "
                "acoustic, majestic."),
}
traccia, desc = STRATI[STRATO]
t0 = time.time()
from acestep.handler import AceStepHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music
from acestep.model_downloader import ensure_main_model, ensure_dit_model
ck = os.path.join(ACE, "checkpoints")
print(ensure_main_model(ck), ensure_dit_model("acestep-v15-base", ck), flush=True)
dit = AceStepHandler()
msg, ok = dit.initialize_service(project_root=ACE, config_path="acestep-v15-base", device="cpu", offload_to_cpu=False)
print("DiT:", ok, msg, flush=True)
if not ok: sys.exit(1)
params = GenerationParams(task_type="lego", src_audio=SRC, instruction=f"Generate the {traccia} track based on the audio context:",
                          caption=desc, lyrics="[Instrumental]", instrumental=True, vocal_language="unknown", bpm=108,
                          keyscale="D minor", timesignature="4", duration=120.0, repainting_start=0.0, repainting_end=-1,
                          inference_steps=30, guidance_scale=6.0, seed=SEED, thinking=False, use_cot_metas=False,
                          use_cot_caption=False, use_cot_language=False)
config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[SEED], audio_format="wav")
t1 = time.time()
res = generate_music(dit, None, params=params, config=config, save_dir=os.path.join(OUT, "grezzi"))
print("esito:", res.success, res.status_message, flush=True)
if not res.success or not res.audios: sys.exit(2)
shutil.copy(res.audios[0]["path"], os.path.join(OUT, f"strato-{STRATO}.wav"))
json.dump({"strato": STRATO, "traccia": traccia, "descrizione": desc, "seme": SEED, "passi": 30, "cfg": 6.0,
           "generazione_s": round(time.time() - t1, 1), "totale_s": round(time.time() - t0, 1)},
          open(os.path.join(OUT, f"strato-{STRATO}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
