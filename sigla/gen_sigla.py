# Prove di sigla strumentale con ACE-Step 1.5 (licenza MIT), costruite sulla mappa del video.
# Uso: python gen_sigla.py <cartella ACE-Step> <variante A|B|C> <cartella di uscita> <lm: 0.6B oppure no>
import json, os, sys, time, shutil, glob

ACE, VAR, OUT, LM = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, ACE)
os.chdir(ACE)

STRUMENTI = ("tabor and frame drums, shawm and bombarde, wooden recorder and wooden transverse flute, "
             "medieval vielle fiddle, hurdy-gurdy drone, lute, psaltery, church bells")
VARIANTI = {
    "A": dict(seed=1256, key="D minor",
              caption="Solemn processional medieval instrumental, 13th-century Italian early music ensemble. Steady marching "
                      f"{STRUMENTI}. Acoustic, historically informed performance, stately and majestic, slow build from a quiet "
                      "drum march to a grand climax with ringing bells."),
    "B": dict(seed=1282, key="G major",
              caption="Lively medieval estampie and saltarello dance, instrumental early music ensemble of the 13th century: "
                      f"{STRUMENTI}. Acoustic, joyful, energetic, festive Italian market dance with bright wooden flute runs "
                      "and driving tabor rhythms."),
    "C": dict(seed=1176, key="D minor",
              caption="Epic medieval instrumental played only on authentic 13th-century acoustic instruments: thundering "
                      f"{STRUMENTI}. Early music ensemble, heroic and dramatic, battle intensity, huge frame drum hits, "
                      "raw shawm fanfares."),
}
# struttura della mappa: 120 BPM, 4/4, battuta = 2 s, 60 battute = 120 s
STRUTTURA = """[Intro - 4 bars - lone tabor march growing louder, ends on one heavy drum hit, then silence]

[Verse 1 - 5 bars - calm gliding flight, soft recorder over hurdy-gurdy drone]

[Verse 2 - 7 bars - bright sunny Palermo, vielle and lute melody]

[Pre-Chorus - 5 bars - lively market dance, psaltery and frame drum]

[Bridge - 5 bars - church bells ringing, rising tension]

[Chorus - 5 bars - full ensemble at maximum, pounding drums and shawms, battle charge]

[Interlude - 5 bars - calm after the battle, soft flute, sea breeze]

[Verse 3 - 8 bars - peaceful work, gentle lute and recorder, slowly building]

[Chorus - 5 bars - climax, main theme, full ensemble with bells, triumphant]

[Chorus - 7 bars - main theme continues, slightly lighter]

[Outro - 4 bars - final cadence, ends on one last tabor stroke]"""
NEGATIVO = "drum kit, orchestral strings, cinematic choir, synthesizer, electric guitar, piano, modern pop production"

v = VARIANTI[VAR]
tempi = {"variante": VAR, "seme": v["seed"], "bpm": 120, "metro": "4/4", "tonalita": v["key"], "durata": 120,
         "descrizione": v["caption"], "struttura": STRUTTURA, "lm": LM}
t0 = time.time()
from acestep.handler import AceStepHandler
from acestep.llm_inference import LLMHandler
from acestep.inference import GenerationParams, GenerationConfig, generate_music

dit = AceStepHandler()
msg, ok = dit.initialize_service(project_root=ACE, config_path="acestep-v15-turbo", device="cpu", offload_to_cpu=False)
print("DiT:", ok, msg, flush=True)
if not ok:
    sys.exit(1)
tempi["caricamento_dit_s"] = round(time.time() - t0, 1)

llm = LLMHandler()
usa_lm = False
if LM != "no":
    t1 = time.time()
    try:
        from acestep.model_downloader import ensure_lm_model
        print(ensure_lm_model(f"acestep-5Hz-lm-{LM}", os.path.join(ACE, "checkpoints")), flush=True)
        msg, usa_lm = llm.initialize(checkpoint_dir=os.path.join(ACE, "checkpoints"), lm_model_path=f"acestep-5Hz-lm-{LM}",
                                     backend="pt", device="cpu", offload_to_cpu=False, dtype=None)
        print("LM:", usa_lm, msg, flush=True)
    except Exception as e:
        print("LM non disponibile:", e, flush=True)
    tempi["caricamento_lm_s"] = round(time.time() - t1, 1)
tempi["lm_usato"] = usa_lm

params = GenerationParams(task_type="text2music", caption=v["caption"], lyrics=STRUTTURA, instrumental=True,
                          vocal_language="unknown", bpm=120, keyscale=v["key"], timesignature="4", duration=120.0,
                          inference_steps=8, guidance_scale=1.0, seed=v["seed"], thinking=usa_lm,
                          use_cot_metas=False, use_cot_caption=False, use_cot_language=False,
                          lm_negative_prompt=NEGATIVO)
config = GenerationConfig(batch_size=1, use_random_seed=False, seeds=[v["seed"]], audio_format="wav")
t2 = time.time()
res = generate_music(dit, llm if usa_lm else None, params=params, config=config, save_dir=os.path.join(OUT, "grezzi"))
tempi["generazione_s"] = round(time.time() - t2, 1)
tempi["totale_s"] = round(time.time() - t0, 1)
print("esito:", res.success, res.status_message, flush=True)
for i, a in enumerate(res.audios):
    p = a.get("path")
    if p and os.path.exists(p):
        shutil.copy(p, os.path.join(OUT, f"sigla-{VAR}.wav"))
        print("salvato", p, flush=True)
json.dump(tempi, open(os.path.join(OUT, f"sigla-{VAR}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(tempi, ensure_ascii=False, indent=1))
if not res.success:
    sys.exit(2)
