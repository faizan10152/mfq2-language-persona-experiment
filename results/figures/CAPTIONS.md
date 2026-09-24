# Figure captions

## fig1_country_means

Figure 1. Mean MFQ-2 foundation scores for the five Spanish-speaking countries. Black: human respondents (Atari et al., 2023, Study 2; n = 1,026). Blue and orange: model responses under an English and a Spanish prompt respectively, each with the matching country persona (n = 50 administrations per cell). Country codes: AR, CH, CO, ME, PE. A model that reproduced human cross-country structure would trace the black line; a model that flattens the personas produces a horizontal line.

## fig2_variance_flattening

Figure 2. Ratio of the model's standard deviation across its 50 administrations to the corresponding human within-country standard deviation, averaged over the five countries. Values below the dashed line indicate a synthetic population less varied than the real one. Every ratio in the study falls below parity. Mistral 7B under an English prompt scores exactly 5.0 on all six Care items in all 300 administrations, giving a ratio of zero.

## fig3_magnitude_vs_accuracy

Figure 3. Left: persona effect size (one-way ANOVA η² across the five country personas, averaged over foundations, Care excluded). Right: ordering accuracy (mean Spearman ρ against the human country ordering, combined permutation test); ✓ marks results significant after Holm correction across the six tests. Rows are sorted by effect size, so the left panel is monotonic by construction and any departure from that order on the right is the finding. Qwen 2.5 7B under a Spanish prompt produces the second-largest effect in the study and the second-worst ordering; Mistral 7B under a Spanish prompt produces a small effect and the most accurate ordering. See the appendix for the Care sensitivity analysis, which affects the Llama 3.1 8B English result.

## fig4_care_ceiling

Figure 4. Distribution of Care scores across all 600 administrations per model. Real respondents average 3.77 with a within-country standard deviation of 0.76. All three models sit at or near the top of the scale, and Mistral 7B under an English prompt returns exactly 5.0 every time, leaving no variance for any country persona to act on. Care is therefore reported separately from the accuracy analysis.