"""Assemble the MFQ-2 prompt for every experimental cell.

A cell is (language, persona):
    language ∈ {en, es}
    persona  ∈ {none, Argentina, Chile, Colombia, Mexico, Peru}
=> 12 cells, identical across models.

Official text (instruction, 36 items, 5 scale labels) comes from
prompts/items_{en,es}.json, i.e. verbatim from Atari et al.'s official
translation .docx files. Everything else (persona sentence, scale header,
JSON-format instruction, Spanish country names) comes from
prompts/templates.json and is the student's design decision.

Usage:
    python src/build_prompts.py            # render all 12 cells to prompts/rendered/
    python src/build_prompts.py --show es Peru
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "prompts"
RENDERED = PROMPTS / "rendered"

LANGUAGES = ["en", "es"]
PERSONAS = ["none", "Argentina", "Chile", "Colombia", "Mexico", "Peru"]


def load(lang: str) -> tuple[dict, dict]:
    items = json.loads((PROMPTS / f"items_{lang}.json").read_text(encoding="utf-8"))
    tmpl = json.loads((PROMPTS / "templates.json").read_text(encoding="utf-8"))[lang]
    return items, tmpl


def build(lang: str, persona: str) -> dict:
    """Return {'system': str|None, 'user': str} for one cell."""
    items, tmpl = load(lang)

    if persona == "none":
        system = tmpl["no_persona_system"]
    else:
        country = tmpl["countries"][persona]
        system = tmpl["persona_system"].format(country=country)

    scale = "\n".join(
        f"{n} = {items['scale_labels'][str(n)]}" for n in range(1, 6)
    )
    body = "\n".join(
        f"{n}. {items['items'][str(n)]}" for n in range(1, 37)
    )

    user = "\n\n".join([
        items["instruction"],
        f"{tmpl['scale_header']}\n{scale}",
        body,
        tmpl["format_instruction"],
    ])

    return {"system": system, "user": user}


def cell_id(lang: str, persona: str) -> str:
    return f"{lang}_{persona}"


def prompt_hash(prompt: dict) -> str:
    """Stable hash of the exact prompt text, logged with every model response so
    a run can always be traced back to the wording that produced it."""
    blob = json.dumps(prompt, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:12]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", nargs=2, metavar=("LANG", "PERSONA"),
                    help="print one rendered prompt instead of writing files")
    args = ap.parse_args()

    if args.show:
        lang, persona = args.show
        p = build(lang, persona)
        print(f"--- system ---\n{p['system']}\n\n--- user ---\n{p['user']}")
        return 0

    RENDERED.mkdir(parents=True, exist_ok=True)
    index = {}
    for lang in LANGUAGES:
        for persona in PERSONAS:
            p = build(lang, persona)
            cid = cell_id(lang, persona)
            h = prompt_hash(p)
            index[cid] = {"language": lang, "persona": persona, "prompt_sha256_12": h}
            text = (f"### CELL {cid}   prompt_sha256_12={h}\n"
                    f"### system: {p['system']!r}\n\n{p['user']}\n")
            (RENDERED / f"{cid}.txt").write_text(text, encoding="utf-8")

    (PROMPTS / "prompt_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"rendered {len(index)} cells -> {RENDERED.relative_to(ROOT)}/")
    for cid, meta in index.items():
        print(f"  {cid:<16} {meta['prompt_sha256_12']}")
    print(f"wrote {(PROMPTS / 'prompt_index.json').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
