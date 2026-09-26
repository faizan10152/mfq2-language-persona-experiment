# Aksoy (2024) — verified against the full paper, 2026-09-26

Read: arXiv:2412.18863v1, full PDF. Earlier text in this paper's Related Work
was written from the abstract alone and understated several things.

## Confirmed

- **No persona.** The system prompt is purely a response-format instruction
  ("For each statement, indicate how well it describes you or your opinions.
  Select one of the following options: ...") plus six rules forbidding
  elaboration, apology, disclaimers and negation. No national or cultural
  persona anywhere. The gap argument in the Introduction is safe.
- **Official MFQ-2 translations** from Atari et al. are used, the same source as
  this study.
- Eight languages: Arabic, Farsi, Japanese, Chinese, English, French, Spanish,
  Russian.

## Corrections to what was previously written

| Claim | Correct version |
|---|---|
| "four models" | GPT-3.5-Turbo, GPT-4o-mini, MistralNeMo 12B-Instruct, Llama 3.1 8B-Instruct — two are commercial API models, only two open-weight |
| implied whole-questionnaire administration | **Each MFQ-2 item is presented as a separate prompt.** This study administers all 36 items in one call. A real methodological difference. |
| — | **100 repetitions** per language per model (this study uses 50, following Münker) |
| — | Instructions were **machine-translated and cross-verified by native speakers** — a direct precedent for the DeepL back-translation used here |

## The gap, stated precisely

For RQ3, Aksoy draws **100 human responses per language** from the Atari et al.
(2023) dataset, for six of the eight languages. The Spanish human group is
therefore a single pooled sample drawn across whichever Spanish-speaking
countries that dataset contains — Argentina, Chile, Colombia, Mexico and Peru.

Aksoy's design treats "Spanish" as one human population. This study asks whether
the five countries inside that population differ from one another, and whether a
persona lets a model track those differences. That is a sharper gap statement
than "the two factors have not been crossed", and it is verifiable from Aksoy's
own method section.

## A finding that motivates the choice of Spanish

Aksoy's Tukey HSD post-hoc tests found that differences involving English were
**not** statistically significant for most foundations, *"except Spanish, where
larger differences were observed in Proportionality, Loyalty, and Authority."*

The largest English--Spanish gaps in the present study are on Loyalty (1.33
scale points for qwen2.5:7b) and Authority (0.45), two of those same three
foundations. Worth one sentence in the Discussion as a convergent result.

## Also relevant to the Discussion

Aksoy reports a significant language x model interaction ($p < 0.001$) and
concludes that "the influence of English varies depending on the model". The
present finding that the language x persona interaction is model-specific
extends that result rather than contradicting it, and should be framed that way.
