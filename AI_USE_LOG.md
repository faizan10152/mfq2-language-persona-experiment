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
