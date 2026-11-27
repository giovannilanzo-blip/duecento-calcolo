# Prova musicale con MusicGen small tramite transformers, in CPU.
import os, sys, scipy.io.wavfile as w
from transformers import AutoProcessor, MusicgenForConditionalGeneration
uscita = sys.argv[1]; os.makedirs(uscita, exist_ok=True)
p = AutoProcessor.from_pretrained("facebook/musicgen-small")
m = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
testo = os.environ["TESTO_MUSICA"]
x = p(text=[testo], padding=True, return_tensors="pt")
a = m.generate(**x, do_sample=True, guidance_scale=3, max_new_tokens=1000)
w.write(os.path.join(uscita, "musicgen-small-medievale-prova.wav"), m.config.audio_encoder.sampling_rate, a[0, 0].numpy())
