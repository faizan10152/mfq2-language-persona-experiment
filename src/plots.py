"""Publication figures.

Run:  python src/plots.py           # -> results/figures/*.png and *.pdf

Design notes (so the choices are defensible, not decorative):
  * Colour encodes ONE thing per figure and never encodes rank. Prompt language
    is the blue/orange pair; model identity is the blue/orange/aqua triple. Both
    sets were validated for colour-vision deficiency and contrast against the
    chart surface before any figure was drawn.
  * Humans are never a "series": they are the reference the models are judged
    against, so they are drawn in ink (near-black) with a distinct marker, not
    in a categorical hue.
  * Every figure carries a caption written for the paper, printed to stdout and
    saved next to the image as a .txt.
  * PNG at 300 dpi for Word, PDF for LaTeX. Width 6.5in fits A4 with margins.
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from item_map import FOUNDATIONS, SPANISH_COUNTRIES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGS = ROOT / "results" / "figures"

# Validated categorical slots (see references/palette.md; checked with
# validate_palette.js --mode light --pairs all).
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
LANG_COLOR = {"en": BLUE, "es": ORANGE}
LANG_LABEL = {"en": "English prompt", "es": "Spanish prompt"}
MODEL_COLOR = {"qwen2.5:7b": BLUE, "llama3.1:8b": ORANGE, "mistral:7b": AQUA}
MODEL_SHORT = {"qwen2.5:7b": "Qwen 2.5 7B", "llama3.1:8b": "Llama 3.1 8B",
               "mistral:7b": "Mistral 7B"}

INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8983"
SURFACE = "#ffffff"

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8,
    "axes.edgecolor": MUTED, "axes.linewidth": 0.6,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.frameon": False, "legend.fontsize": 7.5,
    "axes.spines.top": False, "axes.spines.right": False,
    "grid.color": "#e8e8e4", "grid.linewidth": 0.6,
    "savefig.facecolor": SURFACE,
})

CAPTIONS: dict[str, str] = {}


def save(fig, name: str, caption: str) -> None:
    FIGS.mkdir(parents=True, exist_ok=True)
    for ext in ("png", "pdf"):
        fig.savefig(FIGS / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    (FIGS / f"{name}.txt").write_text(caption, encoding="utf-8")
    CAPTIONS[name] = caption
    plt.close(fig)
    print(f"  {name}.png / .pdf")


# --------------------------------------------------------------------------- #

def fig1_country_means(scores, hmean):
    """Small multiples: model vs human country means, 3 models x 6 foundations."""
    models = [m for m in MODEL_COLOR if m in set(scores.model)]
    fig, axes = plt.subplots(len(models), 6, figsize=(6.5, 1.35 * len(models) + 0.9),
                             sharex=True, sharey="row")
    x = np.arange(5)
    for r, model in enumerate(models):
        for c, f in enumerate(FOUNDATIONS):
            ax = axes[r, c]
            ax.grid(axis="y", zorder=0)
            ax.plot(x, hmean.reindex(SPANISH_COUNTRIES)[f].values, color=INK,
                    lw=1.6, marker="o", ms=3.4, zorder=4,
                    label="Humans" if (r == 0 and c == 0) else None)
            for lang in ("en", "es"):
                g = scores[(scores.model == model) & (scores.language == lang) &
                           (scores.persona != "none")]
                if g.empty:
                    continue
                ax.plot(x, g.groupby("persona")[f].mean().reindex(SPANISH_COUNTRIES).values,
                        color=LANG_COLOR[lang], lw=1.6, marker="s", ms=3.0, zorder=3,
                        label=LANG_LABEL[lang] if (r == 0 and c == 0) else None)
            ax.set_ylim(1, 5.35)
            ax.set_yticks([1, 2, 3, 4, 5])
            if r == 0:
                ax.set_title(f, color=INK, pad=4)
            if c == 0:
                ax.set_ylabel(MODEL_SHORT[model], color=INK, fontsize=7.5)
            ax.set_xticks(x)
            ax.set_xticklabels([c[:2] for c in SPANISH_COUNTRIES], fontsize=6.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Country means: models with a country persona vs. real respondents",
                 fontsize=9.5, color=INK, y=1.005)
    fig.tight_layout()
    save(fig, "fig1_country_means",
         "Figure 1. Mean MFQ-2 foundation scores for the five Spanish-speaking "
         "countries. Black: human respondents (Atari et al., 2023, Study 2; "
         "n = 1,026). Blue and orange: model responses under an English and a "
         "Spanish prompt respectively, each with the matching country persona "
         "(n = 50 administrations per cell). Country codes: AR, CH, CO, ME, PE. "
         "A model that reproduced human cross-country structure would trace the "
         "black line; a model that flattens the personas produces a horizontal line.")


def fig2_flattening(sdr):
    """Within-country SD ratio: how much less varied the synthetic populations are."""
    piv = (sdr.groupby(["model", "language", "foundation"])["sd_ratio"].mean()
           .reset_index())
    models = [m for m in MODEL_COLOR if m in set(piv.model)]
    fig, axes = plt.subplots(1, len(models), figsize=(6.5, 2.5), sharey=True)
    y = np.arange(len(FOUNDATIONS))
    for ax, model in zip(np.atleast_1d(axes), models):
        ax.grid(axis="x", zorder=0)
        for k, lang in enumerate(("en", "es")):
            v = (piv[(piv.model == model) & (piv.language == lang)]
                 .set_index("foundation").reindex(FOUNDATIONS)["sd_ratio"].values)
            ax.barh(y + (0.20 if k == 0 else -0.20), v, height=0.36,
                    color=LANG_COLOR[lang], zorder=3, linewidth=0,
                    label=LANG_LABEL[lang] if model == models[0] else None)
        ax.axvline(1.0, color=INK, lw=1.0, ls=(0, (3, 2)), zorder=4)
        ax.set_yticks(y)
        ax.set_yticklabels(FOUNDATIONS)
        ax.invert_yaxis()
        ax.set_xlim(0, 1.15)
        for k, lang in enumerate(("en", "es")):
            v = (piv[(piv.model == model) & (piv.language == lang)]
                 .set_index("foundation").reindex(FOUNDATIONS)["sd_ratio"].values)
            for i, val in enumerate(v):
                if val < 0.005:      # a zero-length bar is invisible; say so
                    ax.annotate("0.00", (0.012, i + (0.20 if k == 0 else -0.20)),
                                fontsize=6, color=INK2, va="center")
        ax.set_title(MODEL_SHORT[model], color=INK, pad=4)
        ax.set_xlabel("model SD ÷ human SD")
    np.atleast_1d(axes)[-1].annotate("human\nparity", xy=(1.03, 5.1), fontsize=6.2,
                                     color=INK2, ha="left", va="center")
    handles, labels = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, bbox_to_anchor=(0.5, -0.09))
    fig.suptitle("Variance flattening: synthetic populations are less varied than real ones",
                 fontsize=9.5, color=INK, y=1.02)
    fig.tight_layout()
    save(fig, "fig2_variance_flattening",
         "Figure 2. Ratio of the model's standard deviation across its 50 "
         "administrations to the corresponding human within-country standard "
         "deviation, averaged over the five countries. Values below the dashed "
         "line indicate a synthetic population less varied than the real one. "
         "Every ratio in the study falls below parity. Mistral 7B under an "
         "English prompt scores exactly 5.0 on all six Care items in all 300 "
         "administrations, giving a ratio of zero.")


def fig3_dissociation(anova, profile):
    """The novel finding: effect magnitude and ordering accuracy are unrelated.

    Form note: a scatter of six points could not be labelled without collisions,
    and the claim is about RANK disagreement between two measures. Paired bars
    sorted by effect size show that directly -- the left panel is monotonic by
    construction, so any deviation from monotonicity on the right IS the finding.
    """
    eta = (anova[anova.foundation != "Care"]
           .groupby(["model", "language"])["eta2_model"].mean().reset_index())
    d = (profile.merge(eta, on=["model", "language"])
         .sort_values("eta2_model", ascending=True).reset_index(drop=True))
    labels = [f"{MODEL_SHORT[r.model]}  ·  {r.language.upper()}" for _, r in d.iterrows()]
    y = np.arange(len(d))
    colors = [LANG_COLOR[r.language] for _, r in d.iterrows()]

    fig, axes = plt.subplots(1, 2, figsize=(6.5, 2.9), sharey=True)
    axes[0].barh(y, d.eta2_model, height=0.62, color=colors, linewidth=0, zorder=3)
    axes[0].set_xlabel("persona effect size  (mean η²)")
    axes[0].set_title("How much the persona moves the model", color=INK, pad=6)
    for i, v in enumerate(d.eta2_model):
        axes[0].annotate(f"{v:.3f}", (v, i), xytext=(4, 0), textcoords="offset points",
                         va="center", fontsize=6.6, color=INK2)
    axes[0].set_xlim(0, max(d.eta2_model) * 1.30)

    axes[1].barh(y, d.mean_rho, height=0.62, color=colors, linewidth=0, zorder=3)
    axes[1].axvline(0, color=MUTED, lw=0.8)
    axes[1].set_xlabel("ordering accuracy  (mean ρ vs. humans)")
    axes[1].set_title("Whether it moves it in the right direction", color=INK, pad=6)
    for i, r in d.iterrows():
        mark = f"{r.mean_rho:.2f}" + ("  ✓" if r.significant_holm else "")
        axes[1].annotate(mark, (r.mean_rho, i), xytext=(4, 0),
                         textcoords="offset points", va="center",
                         fontsize=6.6, color=INK if r.significant_holm else INK2)
    axes[1].set_xlim(0, 0.92)

    for ax in axes:
        ax.grid(axis="x", zorder=0)
        ax.set_yticks(y)
        ax.set_yticklabels(labels, fontsize=7)
    handles = [plt.Rectangle((0, 0), 1, 1, color=LANG_COLOR[l]) for l in ("en", "es")]
    fig.legend(handles, [LANG_LABEL[l] for l in ("en", "es")], loc="lower center",
               ncol=2, bbox_to_anchor=(0.5, -0.10))
    axes[1].annotate("✓ significant after Holm", (0.98, 0.04), xycoords="axes fraction",
                     ha="right", fontsize=6.4, color=MUTED)
    fig.suptitle("Effect magnitude and ordering accuracy are dissociated",
                 fontsize=9.5, color=INK, y=1.02)
    fig.tight_layout()
    save(fig, "fig3_magnitude_vs_accuracy",
         "Figure 3. Left: persona effect size (one-way ANOVA η² across the five "
         "country personas, averaged over foundations, Care excluded). Right: "
         "ordering accuracy (mean Spearman ρ against the human country ordering, "
         "combined permutation test); ✓ marks results significant after Holm "
         "correction across the six tests. Rows are sorted by effect size, so the "
         "left panel is monotonic by construction and any departure from that "
         "order on the right is the finding. Qwen 2.5 7B under a Spanish prompt "
         "produces the second-largest effect in the study and the second-worst "
         "ordering; Mistral 7B under a Spanish prompt produces a small effect and "
         "the most accurate ordering. See the appendix for the Care sensitivity "
         "analysis, which affects the Llama 3.1 8B English result.")


def fig4_care_ceiling(scores, human_care):
    """The vivid illustration of collapse."""
    models = [m for m in MODEL_COLOR if m in set(scores.model)]
    fig, axes = plt.subplots(1, len(models), figsize=(6.5, 2.3), sharey=True)
    bins = np.arange(1, 5.01 + 1 / 6, 1 / 6)
    hc = human_care.values
    for ax, model in zip(np.atleast_1d(axes), models):
        ax.grid(axis="y", zorder=0)
        ax.hist(hc, bins=bins, weights=np.full(len(hc), 1 / len(hc)), zorder=2,
                color="#d8d7d2", edgecolor="none",
                label="Human respondents" if model == models[0] else None)
        for lang in ("en", "es"):
            v = scores[(scores.model == model) & (scores.language == lang)]["Care"].values
            ax.hist(v, bins=bins, weights=np.full(len(v), 1 / len(v)),
                    histtype="step", lw=1.8, color=LANG_COLOR[lang], zorder=4,
                    label=LANG_LABEL[lang] if model == models[0] else None)
        ax.set_title(MODEL_SHORT[model], color=INK, pad=4)
        ax.set_xlabel("Care score")
        ax.set_xlim(1, 5.15)
        ax.set_ylim(0, 1.02)
    np.atleast_1d(axes)[0].set_ylabel("proportion of responses")
    handles, labels = np.atleast_1d(axes)[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, bbox_to_anchor=(0.5, -0.13))
    fig.suptitle("Ceiling collapse on Care (human mean 3.77, SD 0.76)",
                 fontsize=9.5, color=INK, y=1.02)
    fig.tight_layout()
    save(fig, "fig4_care_ceiling",
         "Figure 4. Distribution of Care scores across all 600 administrations "
         "per model. Real respondents average 3.77 with a within-country standard "
         "deviation of 0.76. All three models sit at or near the top of the scale, "
         "and Mistral 7B under an English prompt returns exactly 5.0 every time, "
         "leaving no variance for any country persona to act on. Care is therefore "
         "reported separately from the accuracy analysis.")


def main() -> int:
    need = ["model_scores.csv", "sd_ratio.csv", "persona_anova.csv", "profile_test.csv"]
    missing = [n for n in need if not (TABLES / n).exists()]
    if missing:
        raise SystemExit(f"missing {missing} — run src/analyze.py first")

    scores = pd.read_csv(TABLES / "model_scores.csv")
    human = pd.read_csv(ROOT / "data" / "processed" / "human_respondents.csv")
    hmean = human.groupby("country_label")[FOUNDATIONS].mean()

    print("writing figures ->", FIGS.relative_to(ROOT))
    fig1_country_means(scores, hmean)
    fig2_flattening(pd.read_csv(TABLES / "sd_ratio.csv"))
    fig3_dissociation(pd.read_csv(TABLES / "persona_anova.csv"),
                      pd.read_csv(TABLES / "profile_test.csv"))
    fig4_care_ceiling(scores, human["Care"])

    (FIGS / "CAPTIONS.md").write_text(
        "# Figure captions\n\n" + "\n\n".join(
            f"## {k}\n\n{v}" for k, v in CAPTIONS.items()), encoding="utf-8")
    print(f"captions -> {(FIGS / 'CAPTIONS.md').relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
