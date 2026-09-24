# Analytic choice: excluding Care from the ordering test

**This choice changes one of the three headline results. It must be disclosed in
the paper, with the sensitivity analysis below reported alongside.**

A commit message dated 2026-09-24 ("Replace underpowered ordering test...")
states "conclusion unchanged if included". **That is wrong** — it was written
before the robustness check was read. This note is the correction.

## The choice

`profile_test()` measures whether a model reproduces the human ordering of the
five countries, combining foundations into one statistic per model x language.
Care is **excluded** from the primary version.

## Why Care is excluded (the reason, stated before the outcome was known)

Care is variance-collapsed in English for all three models:

| model | lang | pooled model SD | SD ratio vs human | degenerate |
|---|---|---|---|---|
| mistral:7b  | en | 0.000 | 0.000 | **yes — all 300 administrations scored exactly 5.0** |
| llama3.1:8b | en | 0.071 | 0.093 | no |
| qwen2.5:7b  | en | 0.074 | 0.097 | no |

Where every country mean is identical there is no ordering to reproduce, so a
rank correlation is undefined (mistral) or is ranking numerical noise (the other
two, at ~9% of human variance). Including such a cell does not test accuracy; it
injects a random number into the average.

Sequence of events, which matters for whether this is a defensible
pre-specification rather than a result-driven choice:

1. The Care ceiling was flagged from the smoke test (2 samples/cell), long before
   any ordering test existed.
2. The student decided Care should be handled separately.
3. `profile_test()` was then written with `exclude=["Care"]`.
4. Only afterwards was the with-Care sensitivity analysis run.

## Sensitivity analysis — the honest version

| model | lang | mean rho (no Care) | p | mean rho (with Care) | p | changes? |
|---|---|---|---|---|---|---|
| llama3.1:8b | en | 0.580 | 0.0088 | 0.389 | 0.0596 | **YES — significant becomes n.s.** |
| llama3.1:8b | es | 0.600 | 0.0064 | 0.550 | 0.0064 | no |
| mistral:7b  | en | 0.050 | 0.8291 | 0.050 | 0.8260 | no |
| mistral:7b  | es | 0.664 | 0.0018 | 0.537 | 0.0063 | no |
| qwen2.5:7b  | en | 0.040 | 0.8972 | 0.071 | 0.7464 | no |
| qwen2.5:7b  | es | 0.160 | 0.4886 | 0.000 | 1.0000 | no |

(p shown is the uncorrected permutation p; Holm is applied across the six tests.)

**Llama 3.1 8B in English is the one result that flips**, and it flips across the
0.05 line rather than dramatically: p = 0.009 to p = 0.060. Its Spanish result and
both Mistral results are unaffected.

## What the paper must say

Do not report only the favourable version. State the exclusion, the reason, and
that Llama's English result is contingent on it. The defensible claim is the
conservative one:

> Llama 3.1 8B reproduces human country orderings in Spanish robustly, and in
> English only when the variance-collapsed Care foundation is excluded.

This is precisely the "signal vs artifact / analytic flexibility" tension from the
synthesis lecture, arising in the student's own analysis. It is better used as a
worked example in the Limitations section than hidden.
