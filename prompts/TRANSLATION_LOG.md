# Translation log

Covers every Spanish string in the prompts that does **not** come from Atari et al.'s
official MFQ-2 translation. The instruction sentence, the 36 items and the 5 response
labels are official and were extracted verbatim by `src/parse_docx.py`; they are not
listed here and were not touched.

Everything below lives in `prompts/templates.json`.

**Status: UNVERIFIED.** The Spanish was drafted by Claude Opus 5 (Claude Code) on
2026-09-21/22 and the back-translations below are literal glosses by the same tool.
Drafting and back-translating with one tool is not an independent check. Before the
runs, the student must verify each string — ideally by round-tripping it through an
independent engine (DeepL) and recording that result in the "Independent check"
column — and is responsible for any uncorrected error.

## Strings

| # | Purpose | English (source) | Spanish (drafted) | Literal back-translation | Independent check |
|---|---|---|---|---|---|
| 1 | Persona sentence | You are a person from {country}. | Usted es una persona de {country}. | "You are a person from {country}." (formal *usted*) | *pending* |
| 2 | Baseline system message (no persona) | You are a person answering a survey. | Usted es una persona que responde a una encuesta. | "You are a person who is answering a survey." (formal *usted*) | *pending* |
| 3 | Scale header | Use the following scale: | Utilice la siguiente escala: | "Use the following scale:" (formal *usted*) | *pending* |
| 4 | Format instruction | Answer every statement. Respond with ONLY a single JSON object mapping each statement number to an integer from 1 to 5, and no other text. Example format: {...} | Responda a todas las afirmaciones. Responda ÚNICAMENTE con un solo objeto JSON que asocie el número de cada afirmación con un número entero del 1 al 5, sin ningún otro texto. Formato de ejemplo: {...} | "Answer all the statements. Respond ONLY with a single JSON object that associates the number of each statement with a whole number from 1 to 5, without any other text. Example format: {...}" | *pending* |

## Country names

English prompts use the English exonyms; Spanish prompts use the Spanish endonyms.

| Persona | English | Spanish |
|---|---|---|
| Argentina | Argentina | Argentina |
| Chile | Chile | Chile |
| Colombia | Colombia | Colombia |
| Mexico | Mexico | **México** |
| Peru | Peru | **Perú** |

Note that the human data file spells Colombia as `Columbia`; that is a data-file
artefact only and never appears in a prompt (see `src/item_map.py`).

## Resolved: register (decided 2026-09-22)

The official Spanish instruction and response labels address the respondent with the
**formal** *usted*. An earlier draft of the persona sentence used the informal *tú*
("Eres una persona de Perú"), mixing two registers inside one prompt. Register is not
cosmetic in Spanish — it encodes social distance and could plausibly shift responses
on the very foundations under study, Authority in particular.

**Decision: formal *usted* throughout**, so the persona sentence matches the register
of the official text. State this explicitly in the Method section.

## Resolved: baseline structure (decided 2026-09-22)

An earlier draft gave the persona cells a system message and the no-persona cells none
at all, so the baseline differed from the persona conditions structurally as well as in
content.

**Decision: all 12 cells carry a system message.** The baseline gets a contentless one
that is structurally parallel to the persona sentence — "You are a person answering a
survey." / "Usted es una persona que responde a una encuesta." — so the only thing
varying across persona conditions is the country cue itself, and any persona effect is
attributable to the country rather than to the presence of a system message.

## Resolved: persona wording vs Münker (decided 2026-09-22)

Münker (2025) describes his persona prompt but never prints it, and his code is only
available on request. The English persona sentence `You are a person from {country}.`
implements his description and is kept. Design-level comparability may be claimed;
string-level replication may not. Full analysis, including a divergence in MFQ-2
item 27, is in `prompts/MUNKER_COMPARABILITY.md`.
