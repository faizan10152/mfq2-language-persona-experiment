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
| 2026-09-22 | Claude Code (Claude Opus 5) | `config.json` — run configuration (models, 50 samples/cell, temperature 0.8, retry budget). Values chosen by the student; file written by the tool. |
| 2026-09-22 | Claude Code (Claude Opus 5) | Read Münker (2025), arXiv:2507.10073v2, and wrote `prompts/MUNKER_COMPARABILITY.md` — what the paper does/does not specify, the item-27 divergence, and two text errors in that paper. Findings are quotations and comparisons against sources, to be re-checked by the student before citing. |
| 2026-09-22 | Claude Code (Claude Opus 5) | `src/run_models.py` — Ollama client, strict 36-item JSON validation with per-failure diagnostics, deterministic per-sample seeds, retry-and-log, resumable JSONL output, model digest/quantization capture. Parser tested against 15 simulated failure modes. |
| 2026-09-22 | Claude Code (Claude Opus 5) | `src/analyze.py` — all four metric families from the analysis plan (distance to humans, between-country spread + Spearman + ANOVA eta-squared, within-country SD ratio, language effect), tidy CSV outputs, parse-rate table, incomplete-cell warning. Metric formulas are stated in each function's docstring for quoting in the Method section. |
| 2026-09-23 | Claude Code (Claude Opus 5) | Fixed invalid Spearman p-values in `src/analyze.py` (scipy's asymptotic approximation is wrong at n=5; replaced with exact permutation null over 5! orderings) and added Holm-Bonferroni family-wise correction to both the rank-correlation and ANOVA tables. |
| 2026-09-24 | Claude Code (Claude Opus 5) | Retracted an incorrect tool-generated finding about Llama being slower in Spanish; see `results/RETRACTED_tokenizer_finding.md`. Direct token measurement and a controlled re-test both contradicted it. An example of why tool output must be verified before it reaches the paper. |
| 2026-09-24 | Claude Code (Claude Opus 5) | Fixed a false-positive bug in `src/analyze.py`: a fully degenerate cell (mistral:7b / en / Care, all 300 administrations scoring exactly 5.0) produced rho = NaN, which the exact-p code silently converted to p = 0.0 and reported as the study's only significant rank correlation. Degenerate cells are now excluded from the test family. |
| 2026-09-24 | Claude Code (Claude Opus 5) | Added `profile_test()` (combined permutation test of ordering accuracy, one per model x language, replacing 36 underpowered per-foundation Spearman tests) and `ceiling_report()` to `src/analyze.py`. Design of the test responds to the student's decision to handle Care separately. |
| 2026-09-24 | Claude Code (Claude Opus 5) | Corrected a false claim in a tool-written commit message ("conclusion unchanged if included"); the Care exclusion does flip llama3.1:8b/en across p = 0.05. Documented in `results/ANALYTIC_CHOICE_care.md` with the full sensitivity analysis. |
| 2026-09-24 | Claude Code (Claude Opus 5) | `src/plots.py` — four publication figures (PNG 300dpi + PDF) with captions. Palette validated for colour-vision deficiency and contrast before drawing; figures rendered and inspected, then Figure 3 reformed from a scatter to paired bars after label collisions, and Figure 4 given the human distribution as a reference. |
| 2026-09-24 | Claude Code (Claude Opus 5) | `paper/references.bib` — 11 references, each verified against a primary source (arXiv API, ACL Anthology, publisher record) with the verification method noted per entry. Two seminar readings could not be confirmed and are marked do-not-cite rather than guessed. |
| 2026-09-26 | Claude Code (Claude Opus 5) | Read Aksoy (2024) in full and corrected Related Work claims previously written from the abstract; findings recorded in `paper/AKSOY_VERIFICATION.md`. |
