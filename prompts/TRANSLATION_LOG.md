# Translation log

Covers every Spanish string in the prompts that does **not** come from Atari et al.'s
official MFQ-2 translation. The instruction sentence, the 36 items and the 5 response
labels are official and were extracted verbatim by `src/parse_docx.py`; they are not
listed here and were not touched.

Everything below lives in `prompts/templates.json`.

**Status: UNVERIFIED.** The Spanish was drafted by Claude Opus 5 (Claude Code) on
2026-09-21 and the back-translations below are literal glosses by the same tool.
Drafting and back-translating with one tool is not an independent check. Before the
runs, the student must verify each string — ideally by round-tripping it through an
independent engine (DeepL) and recording that result in the "Independent check"
column — and is responsible for any uncorrected error.

## Strings

| # | Purpose | English (source) | Spanish (drafted) | Literal back-translation | Independent check |
|---|---|---|---|---|---|
| 1 | Persona sentence | You are a person from {country}. | Eres una persona de {country}. | "You are a person from {country}." (informal *tú*) | *pending* |
| 2 | Scale header | Use the following scale: | Utilice la siguiente escala: | "Use the following scale:" (formal *usted*) | *pending* |
| 3 | Format instruction | Answer every statement. Respond with ONLY a single JSON object mapping each statement number to an integer from 1 to 5, and no other text. Example format: {...} | Responda a todas las afirmaciones. Responda ÚNICAMENTE con un solo objeto JSON que asocie el número de cada afirmación con un número entero del 1 al 5, sin ningún otro texto. Formato de ejemplo: {...} | "Answer all the statements. Respond ONLY with a single JSON object that associates the number of each statement with a whole number from 1 to 5, without any other text. Example format: {...}" | *pending* |

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

## Open issue: register mismatch (needs a decision)

The official Spanish instruction and response labels address the respondent with the
**formal** *usted* ("indique en qué medida cada afirmación **lo describe a usted**").
Strings 2 and 3 follow that register. String 1, the persona sentence, currently uses
the **informal** *tú* ("**Eres** una persona de Perú").

This is inconsistent within a single prompt, and register is not cosmetic in Spanish:
it encodes social distance and may plausibly shift responses on exactly the
foundations under study (Authority in particular). Three options:

1. **Match the official register** — `Usted es una persona de {country}.`
   Internally consistent; the whole prompt speaks to the model as *usted*.
2. **Keep the informal** — `Eres una persona de {country}.`
   Closer to how a system prompt normally addresses an assistant, and closer to the
   flat English "You are...", which marks no register at all.
3. **Run both** as a robustness check on one model, and report the difference.

Option 1 is the conservative choice and the easiest to defend in the Method section.
Whatever is chosen must be stated explicitly in the paper — the seminar's takeaway
"report the FULL configuration" covers prompt register.

## Not yet verified against Münker (2025)

The English persona sentence "You are a person from {country}." is a plausible
minimal persona cue, but it has **not** been checked against the wording Münker
(2025) actually used. If comparability with Münker is a claim the paper wants to
make, the student must read the exact prompt out of that paper (or its repository)
and reconcile it here. Do not assert comparability until that is done.
