"""Administer the MFQ-2 to local Ollama models and log every response.

One call = one complete questionnaire (36 items) = one simulated respondent.

Design points that matter for the paper:
  * Every response is logged raw, whether it parsed or not. Parse failure is a
    result in its own right (small models may fail more often in Spanish), so
    failures are never silently dropped.
  * Each sample gets a deterministic seed derived from
    (model, language, persona, sample_idx, attempt), so the whole run is
    reproducible from this file plus config.json.
  * Model digest and quantization level are captured per model and written to
    results/run_metadata.json. "Llama 3.1 8B" is ambiguous; a digest is not.
  * The run is resumable: samples already present in the JSONL are skipped, so
    an interrupted run continues rather than restarting.

Usage:
    python src/run_models.py --smoke          # 2 samples x 2 cells, 1 model
    python src/run_models.py                  # the full grid from config.json
    python src/run_models.py --models qwen2.5:7b --languages es
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_prompts import build, prompt_hash  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "config.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "results" / "raw_jsonl"
META_PATH = ROOT / "results" / "run_metadata.json"

OLLAMA = "http://127.0.0.1:11434"
N_ITEMS = 36


# --------------------------------------------------------------------------- #
# Ollama
# --------------------------------------------------------------------------- #

def server_version() -> str:
    return requests.get(f"{OLLAMA}/api/version", timeout=10).json().get("version", "?")


def model_info(model: str) -> dict:
    """Digest, quantization and parameter size for one model. These go in the paper."""
    r = requests.post(f"{OLLAMA}/api/show", json={"model": model}, timeout=60)
    r.raise_for_status()
    d = r.json()
    details = d.get("details", {})
    tags = requests.get(f"{OLLAMA}/api/tags", timeout=30).json().get("models", [])
    digest = next((m.get("digest", "") for m in tags if m.get("name") == model), "")
    return {
        "model": model,
        "digest": digest,
        "family": details.get("family"),
        "parameter_size": details.get("parameter_size"),
        "quantization_level": details.get("quantization_level"),
        "modelfile_parameters": d.get("parameters"),
    }


def chat(model: str, system: str, user: str, options: dict, timeout: int) -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={"model": model, "messages": messages, "stream": False, "options": options},
        timeout=timeout,
    )
    r.raise_for_status()
    return r.json()


# --------------------------------------------------------------------------- #
# Parsing
# --------------------------------------------------------------------------- #

def extract_json(text: str) -> tuple[dict | None, str]:
    """Return (object, how). `how` records whether the model obeyed the format
    instruction exactly ('clean') or needed rescuing ('extracted'), which is
    itself a measure of instruction-following worth reporting."""
    t = text.strip()
    try:
        return json.loads(t), "clean"
    except json.JSONDecodeError:
        pass
    # first balanced {...} block, tolerating prose or ``` fences around it
    start = t.find("{")
    if start == -1:
        return None, "no_json"
    depth = 0
    for i in range(start, len(t)):
        if t[i] == "{":
            depth += 1
        elif t[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(t[start:i + 1]), "extracted"
                except json.JSONDecodeError:
                    return None, "malformed"
    return None, "unbalanced"


def validate(obj) -> tuple[dict | None, str]:
    """Strict: exactly the keys "1".."36", each an integer 1-5."""
    if not isinstance(obj, dict):
        return None, "not_an_object"
    out: dict[int, int] = {}
    for n in range(1, N_ITEMS + 1):
        if str(n) in obj:
            v = obj[str(n)]
        elif n in obj:
            v = obj[n]
        else:
            return None, f"missing_item_{n}"
        if isinstance(v, bool):
            return None, f"bool_item_{n}"
        if isinstance(v, str):
            v = v.strip()
            if not v.lstrip("-").isdigit():
                return None, f"non_numeric_item_{n}"
            v = int(v)
        if isinstance(v, float):
            if v != int(v):
                return None, f"non_integer_item_{n}"
            v = int(v)
        if not isinstance(v, int):
            return None, f"non_numeric_item_{n}"
        if not 1 <= v <= 5:
            return None, f"out_of_range_item_{n}"
        out[n] = v
    extra = [k for k in obj if str(k) not in {str(i) for i in range(1, N_ITEMS + 1)}]
    if extra:
        return None, f"extra_keys_{','.join(map(str, extra[:3]))}"
    return out, "ok"


# --------------------------------------------------------------------------- #
# Run
# --------------------------------------------------------------------------- #

def stable_seed(*parts) -> int:
    h = hashlib.sha256("|".join(map(str, parts)).encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big") % (2 ** 31 - 1)


def jsonl_path(model: str) -> Path:
    return OUT_DIR / f"{model.replace(':', '_').replace('/', '_')}.jsonl"


def already_done(path: Path) -> set[tuple[str, str, int]]:
    done: set[tuple[str, str, int]] = set()
    if not path.exists():
        return done
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError:
                continue
            done.add((r["language"], r["persona"], r["sample_id"]))
    return done


def run_cell_sample(model: str, lang: str, persona: str, sample_id: int,
                    cfg: dict, timeout: int) -> dict:
    prompt = build(lang, persona)
    phash = prompt_hash(prompt)
    max_retries = cfg["max_parse_retries"]

    attempts = []
    parsed, status = None, "never_ran"
    for attempt in range(max_retries + 1):
        seed = stable_seed(model, lang, persona, sample_id, attempt)
        options = {
            "temperature": cfg["sampling"]["temperature"],
            "seed": seed,
            "num_ctx": cfg["sampling"]["num_ctx"],
            "num_predict": cfg["sampling"]["num_predict"],
        }
        if cfg["sampling"].get("top_p") is not None:
            options["top_p"] = cfg["sampling"]["top_p"]

        t0 = time.time()
        try:
            resp = chat(model, prompt["system"], prompt["user"], options, timeout)
            raw = resp.get("message", {}).get("content", "")
            err = None
            eval_count = resp.get("eval_count")
            # Prompt token count: lets the paper state tokenizer cost in tokens
            # rather than inferring it from wall-clock seconds.
            prompt_eval_count = resp.get("prompt_eval_count")
        except Exception as exc:  # network / timeout / server error
            raw, err, eval_count, prompt_eval_count = "", f"{type(exc).__name__}: {exc}", None, None
        elapsed = round(time.time() - t0, 2)

        obj, how = (None, "request_failed") if err else extract_json(raw)
        if obj is not None:
            parsed, status = validate(obj)
        else:
            parsed, status = None, how

        attempts.append({
            "attempt": attempt, "seed": seed, "raw_text": raw,
            "extract_mode": how, "status": status,
            "request_error": err, "seconds": elapsed, "eval_count": eval_count,
            "prompt_eval_count": prompt_eval_count,
        })
        if parsed is not None:
            break

    return {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "model": model,
        "language": lang,
        "persona": persona,
        "sample_id": sample_id,
        "prompt_sha256_12": phash,
        "temperature": cfg["sampling"]["temperature"],
        "num_ctx": cfg["sampling"]["num_ctx"],
        "n_attempts": len(attempts),
        "n_retries": len(attempts) - 1,
        "final_status": status,
        "parsed": parsed,
        "attempts": attempts,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+")
    ap.add_argument("--languages", nargs="+")
    ap.add_argument("--personas", nargs="+")
    ap.add_argument("--samples", type=int)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--smoke", action="store_true",
                    help="2 samples on 2 cells of the first model, for inspection")
    args = ap.parse_args()

    cfg = json.loads(json.dumps(CONFIG))  # copy
    models = args.models or cfg["models"]
    languages = args.languages or cfg["languages"]
    personas = args.personas or cfg["personas"]
    samples = args.samples if args.samples is not None else cfg["samples_per_cell"]

    if args.smoke:
        models = models[:1]
        languages = ["en", "es"]
        personas = ["none", "Peru"]
        samples = 2

    try:
        ver = server_version()
    except Exception as exc:
        print(f"Cannot reach Ollama at {OLLAMA}: {exc}")
        print("Start it by opening the Ollama app, then retry.")
        return 1

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    meta = {
        "ollama_version": ver,
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "config": cfg,
        "models": {},
    }
    for m in models:
        try:
            meta["models"][m] = model_info(m)
        except Exception as exc:
            print(f"!! model '{m}' not available: {exc}")
            print(f"   pull it first:  ollama pull {m}")
            return 1
    META_PATH.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    print(f"Ollama {ver}")
    for m, info in meta["models"].items():
        print(f"  {m:<16} digest={info['digest'][:12]}  "
              f"{info['parameter_size']}  {info['quantization_level']}")
    total = len(models) * len(languages) * len(personas) * samples
    print(f"\ngrid: {len(models)} models x {len(languages)} languages x "
          f"{len(personas)} personas x {samples} samples = {total} calls\n")

    n_done = n_fail = 0
    t_start = time.time()
    for model in models:
        path = jsonl_path(model)
        done = already_done(path)
        with path.open("a", encoding="utf-8") as fh:
            for lang in languages:
                for persona in personas:
                    for sid in range(samples):
                        if (lang, persona, sid) in done:
                            continue
                        rec = run_cell_sample(model, lang, persona, sid, cfg, args.timeout)
                        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        fh.flush()
                        n_done += 1
                        ok = rec["parsed"] is not None
                        n_fail += (not ok)
                        secs = rec["attempts"][-1]["seconds"]
                        print(f"  {model:<14} {lang} {persona:<10} #{sid:<3} "
                              f"{'ok ' if ok else 'FAIL'} "
                              f"{rec['final_status']:<18} {secs:>6.1f}s "
                              f"retries={rec['n_retries']}")

    mins = (time.time() - t_start) / 60
    print(f"\n{n_done} calls in {mins:.1f} min "
          f"({n_fail} unparseable after retries, "
          f"{(n_done - n_fail) / n_done * 100 if n_done else 0:.1f}% parsed)")
    print(f"raw responses -> {OUT_DIR.relative_to(ROOT)}/")
    print(f"run metadata  -> {META_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
