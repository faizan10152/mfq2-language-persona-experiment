"""Extract the MFQ-2 instruction, 36 items and 5 response labels from the
official translation .docx files shipped in the Atari et al. (2023) OSF project.

Layout of every translation file:
    <instruction paragraph(s)>
    <numbered list paragraph = item text>      (may wrap over several paragraphs)
    <5 response-label paragraphs, each ending in "(1)".."(5)">
    ... repeated 36 times ...

Item paragraphs are identifiable because they carry Word list numbering (<w:numPr>);
continuation lines of a wrapped item do not, and neither do the labels (which are
matched by their trailing "(n)").

Usage:  python src/parse_docx.py            # writes prompts/items_en.json, items_es.json
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import docx

ROOT = Path(__file__).resolve().parents[1]
TRANS_DIR = ROOT / "data" / "raw" / "MFQ2_Translations"
OUT_DIR = ROOT / "prompts"

W_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
LABEL_RE = re.compile(r"\((\d)\)\s*$")

FILES = {
    "en": "English Moral Foundations Questionnaire.docx",
    "es": "Spanish Moral Foundations Questionnaire.docx",
}


def _is_numbered(par) -> bool:
    return par._p.find(f".//{W_NS}numPr") is not None


def parse(path: Path) -> dict:
    doc = docx.Document(path)
    paragraphs = [(p.text.strip(), _is_numbered(p)) for p in doc.paragraphs]
    paragraphs = [(t, n) for t, n in paragraphs if t]

    instruction_parts: list[str] = []
    items: list[str] = []
    scales: list[list[str]] = []

    buf: list[str] = []
    cur_labels: list[str] = []
    seen_first_item = False

    for text, numbered in paragraphs:
        m = LABEL_RE.search(text)
        if m:
            # a response label closes the current item text
            if buf:
                items.append(" ".join(buf))
                buf = []
            cur_labels.append(text)
            if len(cur_labels) == 5:
                scales.append(cur_labels)
                cur_labels = []
            continue

        if numbered:
            seen_first_item = True
            if buf:  # should not happen, but keep the text rather than lose it
                items.append(" ".join(buf))
            buf = [text]
        elif seen_first_item:
            buf.append(text)  # wrapped continuation of the current item
        else:
            instruction_parts.append(text)

    if buf:
        items.append(" ".join(buf))

    # Every item must carry the identical 5-point scale; verify, then keep one copy.
    if not scales:
        raise ValueError(f"{path.name}: no response scale found")
    if any(s != scales[0] for s in scales):
        raise ValueError(f"{path.name}: response labels are not identical across items")

    labels = {}
    for lab in scales[0]:
        n = int(LABEL_RE.search(lab).group(1))
        labels[n] = LABEL_RE.sub("", lab).strip()

    return {
        "source_file": path.name,
        "instruction": " ".join(instruction_parts),
        "items": {i + 1: t for i, t in enumerate(items)},
        "scale_labels": labels,
        "n_items": len(items),
        "n_scale_blocks": len(scales),
    }


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = True
    for lang, fname in FILES.items():
        parsed = parse(TRANS_DIR / fname)
        out = OUT_DIR / f"items_{lang}.json"
        out.write_text(json.dumps(parsed, ensure_ascii=False, indent=2), encoding="utf-8")

        print(f"[{lang}] {fname}")
        print(f"     instruction : {parsed['instruction']}")
        print(f"     items       : {parsed['n_items']} (scale blocks: {parsed['n_scale_blocks']})")
        print(f"     scale       : " + " | ".join(f"{k}={v}" for k, v in sorted(parsed["scale_labels"].items())))
        if parsed["n_items"] != 36 or parsed["n_scale_blocks"] != 36:
            print(f"     !! EXPECTED 36 items and 36 scale blocks")
            ok = False
        if sorted(parsed["scale_labels"]) != [1, 2, 3, 4, 5]:
            print(f"     !! EXPECTED scale points 1..5")
            ok = False
        print(f"     -> {out.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
