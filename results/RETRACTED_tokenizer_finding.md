# RETRACTED: the "Llama is slower in Spanish" finding

**Do not put this in the paper.** It was wrong twice, and the commit message on
`Llama 3.1 8B: full 600-call run` (2026-09-22) still states it as a finding.
This note corrects the record.

## What was claimed

During the Llama run, Spanish cells averaged 18.0s per call against 10.0s for
English (1.80x) while producing *fewer* output tokens. It was claimed that the
extra cost was prefill, i.e. that Llama 3.1's tokenizer encodes Spanish much
less efficiently, and that this was "a measurable indicator of English-centricity
independent of the questionnaire responses."

## Why it was wrong

**1. The tokenizer explanation is false.** Measured directly (identical prompt,
`prompt_eval_count` from the Ollama API):

| model | EN tokens | ES tokens | ES/EN | wall-clock ES/EN during the run |
|---|---|---|---|---|
| qwen2.5:7b  | 767 | 987  | 1.29 | 0.98x |
| llama3.1:8b | 741 | 966  | 1.30 | 1.80x |
| mistral:7b  | 831 | 1169 | 1.41 | 1.02x |

Llama and Qwen have essentially identical encoding costs (1.30 vs 1.29), yet only
Llama slowed. Mistral has the *worst* token ratio (1.41) and no slowdown at all.
Token count cannot explain the timing.

**2. The phenomenon does not reproduce.** Re-running llama3.1:8b on an idle
machine, 5 calls per language, same prompts and settings:

    en: mean 8.72s   [9.8, 8.5, 8.4, 8.4, 8.4]
    es: mean 8.80s   [8.5, 9.9, 8.5, 8.5, 8.6]

Ratio 1.01x. The 1.80x was a transient condition of the machine during that
window, not a property of the model.

## What is still true and reportable

Spanish costs roughly **1.3x more tokens than English** to encode for all three
models (1.41x for Mistral). That is a real, directly measured quantity and is
fine to report as prompt-length information. It says nothing about speed, and
nothing about any model being more or less "English-centric" than another.

## Lesson for the Method section

Wall-clock timing on a laptop that is simultaneously downloading models, running
other work and thermally throttling is not a measurement instrument. Any
timing-based claim needs a controlled re-test before it is written down.
