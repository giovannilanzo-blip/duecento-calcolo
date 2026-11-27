# Terzo campionario: voci documentaristiche italiane progettate con Qwen3-TTS VoiceDesign (nessuna persona reale).
import os, sys, time, json, signal
import numpy as np
import soundfile as sf
TESTO = os.environ["TESTO"]
CODA = " Clear studio recording, broadcast quality, full bandwidth, no background noise, no reverb, standard Italian pronunciation without any foreign accent."
VOCI = {
    "F01-autorevole_pacata": "A mature, authoritative and calm female voice, about 55 years old, Italian native speaker. She narrates a history documentary with composure and gravitas, measured pace, low-medium pitch, precise diction." + CODA,
    "F02-divulgatrice_calda": "A warm and engaging female voice, about 35 years old, Italian native speaker. She presents a popular history documentary, captivating and expressive, with natural intonation, gentle emphasis on key words and moderate pace." + CODA,
    "F03-giovane_luminosa": "A young, bright and lively female voice, about 26 years old, Italian native speaker. She narrates a documentary for young audiences with energy and a smiling tone, crisp diction, dynamic but never rushed." + CODA,
    "F04-profonda_vellutata": "A deep, velvety and rich female voice, low pitch, about 45 years old, Italian native speaker. She narrates a documentary with an intimate, elegant and slightly dramatic tone, slow and confident pace." + CODA,
    "F05-dolce_ragazzi": "A sweet, reassuring and kind female voice, about 38 years old, Italian native speaker. She narrates a history documentary for children and teenagers, warm and clear, patient pace, friendly and encouraging intonation." + CODA,
    "F06-cronista_sobria": "A clear, sober and elegant female voice, about 42 years old, Italian native speaker. She narrates a historical documentary like a news anchor telling a chronicle, neutral and polished, steady rhythm, impeccable diction." + CODA,
    "M01-baritono_pacato": "A calm and authoritative baritone male voice, about 55 years old, Italian native speaker. He narrates a history documentary with composure and gravitas, measured pace, rich low tones, precise diction." + CODA,
    "M02-racconto_storico": "A warm male voice, about 40 years old, Italian native speaker. He tells historical stories in a documentary, engaging and vivid, natural intonation with expressive rises and falls, moderate pace." + CODA,
    "M03-giovane_divulgatore": "A young, clear and friendly male voice, about 28 years old, Italian native speaker. He presents a science and history documentary for students, bright and curious tone, crisp diction, lively but steady pace." + CODA,
    "M04-profonda_solenne": "A very deep, solemn and resonant male voice, bass register, about 60 years old, Italian native speaker. He narrates an epic historical documentary with dramatic gravity, slow pace and powerful emphasis." + CODA,
}
voce, uscita = sys.argv[1], sys.argv[2]
os.makedirs(uscita, exist_ok=True)
import torch
from qwen_tts import Qwen3TTSModel
torch.set_num_threads(os.cpu_count())
m = Qwen3TTSModel.from_pretrained("Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign", device_map="cpu", dtype=torch.bfloat16)
def scaduto(*_):
    raise TimeoutError("generazione troppo lunga")
signal.signal(signal.SIGALRM, scaduto)
tempi = []
for seme in [int(x) for x in os.environ.get("SEMI", "1256,1176").split(",")]:
    torch.manual_seed(seme); t0 = time.time()
    signal.alarm(int(os.environ.get("LIMITE", "900")))
    try:
        wavs, sr = m.generate_voice_design(text=TESTO, language="Italian", instruct=VOCI[voce])
    except TimeoutError as ex:
        print("seme", seme, "scartato:", ex, flush=True); continue
    finally:
        signal.alarm(0)
    wav = np.asarray(wavs[0], dtype=np.float32).squeeze()
    nome = f"{voce}-s{seme}"
    sf.write(os.path.join(uscita, nome + ".wav"), wav, sr)
    tempi.append({"file": nome, "seme": seme, "sr": sr, "durata_audio_s": round(len(wav) / sr, 1),
                  "tempo_cpu_s": round(time.time() - t0, 1), "descrizione": VOCI[voce]})
    print(tempi[-1], flush=True)
json.dump(tempi, open(os.path.join(uscita, f"tempi-{voce}.json"), "w"), indent=1)
