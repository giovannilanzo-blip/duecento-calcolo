"""Genera con stable-diffusion.cpp (CPU) i soggetti di un lotto JSON.
Uso: python3 genera_sdcpp.py <lotto.json> <modello klein|qwen> <indice_scheggia> <numero_schegge> <cartella_uscita> [solo_id,...]"""
import json, subprocess, sys, time, os
from pathlib import Path

lotto, modello, k, n, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), Path(sys.argv[5])
solo = set(sys.argv[6].split(",")) if len(sys.argv) > 6 and sys.argv[6] else None
out.mkdir(parents=True, exist_ok=True)
lavori = [j for j in json.load(open(lotto, encoding="utf-8")) if modello in j.get("modelli", ["klein", "qwen"])]
if solo:
    lavori = [j for j in lavori if j["id"] in solo]
lavori = lavori[k::n]
M = Path("modelli")
BIN = next(str(p) for p in Path("sd").rglob("*") if p.is_file() and p.name in ("sd-cli", "sd"))
print("programma:", BIN, flush=True)
DIM = {"klein": {"2:1": (1024, 512), "16:9": (1024, 576), "1:1": (1024, 1024), "3:4": (768, 1024)},
       "qwen": {"2:1": (768, 384), "16:9": (768, 432), "1:1": (640, 640), "3:4": (576, 768)}}
for j in lavori:
    w, h = DIM[modello][j["ar"]]
    w, h = j.get("dim_" + modello, [w, h])
    dest = out / f"{j['id']}_{modello}.png"
    if modello == "klein":
        cmd = [BIN, "--diffusion-model", str(M / "flux-2-klein-4b-Q4_K_M.gguf"),
               "--vae", str(M / "flux2-vae.safetensors"), "--llm", str(M / "Qwen3-4B-Q4_K_M.gguf"),
               "--cfg-scale", "1.0", "--steps", "4", "--sampling-method", "euler"]
        for r in j.get("ref", []):
            cmd += ["-r", r]
    else:
        cmd = [BIN, "--diffusion-model", str(M / "qwen-image-2512-Q2_K.gguf"),
               "--vae", str(M / "qwen_image_vae.safetensors"), "--llm", str(M / "Qwen2.5-VL-7B-Instruct-Q3_K_M.gguf"),
               "--lora-model-dir", str(M), "--cfg-scale", "1.0", "--steps", "4", "--sampling-method", "euler",
               "--flow-shift", "3", "--mmap"]
    prompt = j["prompt"] + (" <lora:Qwen-Image-2512-Lightning-4steps-V1.0-fp32:1>" if modello == "qwen" else "")
    cmd += ["-p", prompt, "-W", str(w), "-H", str(h), "--seed", str(j.get("seed", 1256)),
            "-t", str(os.cpu_count() or 2), "--vae-tiling", "-o", str(dest)]
    t0 = time.time()
    print(f"=== {j['id']} {w}x{h}", flush=True)
    r = subprocess.run(cmd)
    dt = time.time() - t0
    print(f"=== {j['id']} codice {r.returncode} in {dt:.0f} s", flush=True)
    with open(out / "tempi.txt", "a", encoding="utf-8") as f:
        f.write(f"{j['id']}\t{modello}\t{w}x{h}\t{r.returncode}\t{dt:.0f}s\n")
