# AI-use log

Required for the paper's appendix. Every entry lists the date, the tool by product
name, and exactly what the tool produced. The student has read and verified every
line of the code listed here; the research question, design and interpretation are
the student's own.

| Date | Tool | What it generated / did |
|---|---|---|
| 2026-09-21 | Claude Code (Claude Opus 5) | Project scaffolding: directory layout, Python venv, dependency install. |
| 2026-09-21 | Claude Code (Claude Opus 5) | `src/item_map.py` — MFQ-2 item-number → CSV-column table, foundation scoring key, attention-check criterion, country spelling map. Content derived from Atari et al.'s own `Code_Study2.R` and supplementary Table S1 (see docstring for provenance). |
| 2026-09-21 | Claude Code (Claude Opus 5) | `src/parse_docx.py` — parser for the official MFQ-2 translation .docx files (instruction, 36 items, 5 response labels). |
| 2026-09-21 | Claude Code (Claude Opus 5) | `src/load_human.py` — verification report (item columns, attention checks, scale, missingness, country spellings, first_language) and human baseline computation. |
| 2026-09-21 | Claude Code (Claude Opus 5) | Ad-hoc one-way ANOVA / eta² of the country effect in the human data (reported in the session; to be folded into `src/analyze.py`). |
| 2026-09-22 | Claude Code (Claude Opus 5) | `prompts/templates.json` — non-official prompt strings (persona sentence, scale header, JSON-format instruction, Spanish country names). Wording is a design decision; drafted by the tool, to be confirmed/edited by the student. |
| 2026-09-22 | Claude Code (Claude Opus 5) | `src/build_prompts.py` — assembles the 12 experimental cells from the official item text plus the templates, hashes each prompt for provenance. |
| 2026-09-22 | Claude Code (Claude Opus 5) | Spanish drafts and literal back-translations in `prompts/TRANSLATION_LOG.md`. **Marked UNVERIFIED** — drafted and back-translated by the same tool, so not an independent check; student to verify against an independent engine before the runs. |
