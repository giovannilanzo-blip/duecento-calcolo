# Campionario delle voci maschili italiane: ogni motore legge la stessa frase e registra i tempi in CPU.
import os, sys, time, json, subprocess
import soundfile as sf
TESTO = os.environ.get("TESTO") or ("Nel milleduecentocinquantasei, nella valle del Serchio, i cavalieri di Lucca e di Firenze "
    "caricano la fanteria pisana schierata dietro i pavesi. È la battaglia di Ponte a Serchio, e i Pisani ne escono sconfitti.")
motore, uscita = sys.argv[1], sys.argv[2]
os.makedirs(uscita, exist_ok=True)
tempi = []
def salva(nome, wav, sr, t0):
    p = os.path.join(uscita, nome + ".wav"); sf.write(p, wav, sr)
    dur = len(wav) / sr; sec = time.time() - t0
    tempi.append({"file": nome, "durata_audio_s": round(dur, 1), "tempo_cpu_s": round(sec, 1), "rapporto": round(sec / dur, 2)})
    print(tempi[-1], flush=True)

if motore == "kokoro":
    from kokoro import KPipeline
    import numpy as np
    p = KPipeline(lang_code="i")
    for v in ["im_nicola"]:
        t0 = time.time()
        wav = np.concatenate([a.numpy() if hasattr(a, "numpy") else a for _, _, a in p(TESTO, voice=v, speed=0.95)])
        salva(f"kokoro-{v}", wav, 24000, t0)

elif motore == "mms":
    import torch
    from transformers import VitsModel, AutoTokenizer
    m = VitsModel.from_pretrained("facebook/mms-tts-ita"); tok = AutoTokenizer.from_pretrained("facebook/mms-tts-ita")
    t0 = time.time()
    with torch.no_grad():
        wav = m(**tok(TESTO, return_tensors="pt")).waveform[0].numpy()
    salva("mms-tts-ita", wav, m.config.sampling_rate, t0)

elif motore == "xtts":
    import torch
    from TTS.api import TTS
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
    print("SPEAKERS", list(tts.synthesizer.tts_model.speaker_manager.speakers.keys()), flush=True)
    for s in ["Damien Black", "Viktor Eka", "Craig Gutsy", "Luis Moray", "Marcos Rudaski"]:
        t0 = time.time()
        wav = tts.tts(text=TESTO, speaker=s, language="it")
        salva("xtts-" + s.replace(" ", "_"), __import__("numpy").array(wav), 24000, t0)

elif motore == "parler":
    import torch
    from parler_tts import ParlerTTSForConditionalGeneration
    from transformers import AutoTokenizer
    rid = "parler-tts/parler-tts-mini-multilingual-v1.1"
    m = ParlerTTSForConditionalGeneration.from_pretrained(rid); tok = AutoTokenizer.from_pretrained(rid)
    dtok = AutoTokenizer.from_pretrained(m.config.text_encoder._name_or_path)
    descr = {
        "narratore": "A male speaker with a warm, mid-pitched voice delivers a calm and expressive narration at a moderate pace. The recording is very clear and close, with no background noise.",
        "grave": "A male speaker with a deep, low-pitched voice speaks slowly and clearly, in a storytelling tone. The recording is of very high quality, with no background noise.",
    }
    for k, d in descr.items():
        torch.manual_seed(1256); t0 = time.time()
        a = m.generate(input_ids=dtok(d, return_tensors="pt").input_ids, prompt_input_ids=tok(TESTO, return_tensors="pt").input_ids)
        salva(f"parler-multilingual-{k}", a.cpu().numpy().squeeze(), m.config.sampling_rate, t0)

elif motore == "qwen06":
    import torch
    from qwen_tts import Qwen3TTSModel
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-0.6B-CustomVoice", device_map="cpu", dtype=torch.float32)
    print("SPEAKERS", m.get_supported_speakers(), flush=True)
    for s in ["Uncle_Fu", "Ryan", "Aiden", "Dylan", "Eric"]:
        t0 = time.time()
        wavs, sr = m.generate_custom_voice(text=TESTO, language="Italian", speaker=s)
        salva(f"qwen3tts-0.6B-{s}", wavs[0], sr, t0)

elif motore == "qwen17design":
    import torch
    from qwen_tts import Qwen3TTSModel
    m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.bfloat16)
    descr = {
        "narratore": "Voce maschile adulta italiana, calda e chiara, tono da narratore didattico per ragazzi, ritmo moderato, dizione italiana standard senza accento straniero.",
        "grave": "Voce maschile italiana profonda e matura, tono da documentario storico, lenta e solenne, dizione italiana perfetta.",
    }
    for k, d in descr.items():
        torch.manual_seed(1256); t0 = time.time()
        wavs, sr = m.generate_voice_design(text=TESTO, language="Italian", instruct=d)
        salva(f"qwen3tts-1.7B-design-{k}", wavs[0], sr, t0)

json.dump(tempi, open(os.path.join(uscita, f"tempi-{motore}.json"), "w"), indent=1)
