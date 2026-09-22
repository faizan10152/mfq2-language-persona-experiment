"""Compute every metric in the analysis plan and write tidy CSVs.

Run:  python src/analyze.py            # all models found in results/raw_jsonl/
      python src/analyze.py --models qwen2.5:7b llama3.1:8b

Inputs
  results/raw_jsonl/*.jsonl            one record per questionnaire administration
  data/processed/human_respondents.csv from src/load_human.py

Outputs (results/tables/)
  model_scores.csv        per administration: 6 foundation scores
  parse_rates.csv         per cell: parse rate, retry rate  (a result in itself)
  cell_means.csv          per cell: mean and SD per foundation
  distance_to_humans.csv  metric 1
  spread.csv              metric 2a: between-country spread, model vs human
  rank_correlation.csv    metric 2b: Spearman on country ordering
  persona_anova.csv       metric 2c: persona effect size vs human country effect
  sd_ratio.csv            metric 3: within-country flattening
  language_effect.csv     metric 4

Metric definitions are stated in the docstrings of each function, so the paper's
Method section can quote them exactly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent))
from item_map import FOUNDATION_ITEMS, FOUNDATIONS, SPANISH_COUNTRIES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "results" / "raw_jsonl"
TABLES = ROOT / "results" / "tables"
HUMAN = ROOT / "data" / "processed" / "human_respondents.csv"


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load_model_records(models: list[str] | None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return (scores, attempts) — one row per administration, and per-cell parse stats."""
    rows, meta = [], []
    for path in sorted(RAW.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            r = json.loads(line)
            if models and r["model"] not in models:
                continue
            meta.append({
                "model": r["model"], "language": r["language"], "persona": r["persona"],
                "sample_id": r["sample_id"], "parsed_ok": r["parsed"] is not None,
                "n_retries": r["n_retries"], "final_status": r["final_status"],
                "extract_mode": r["attempts"][-1]["extract_mode"],
                "seconds": r["attempts"][-1]["seconds"],
            })
            if r["parsed"] is None:
                continue
            p = {int(k): v for k, v in r["parsed"].items()}
            row = {"model": r["model"], "language": r["language"],
                   "persona": r["persona"], "sample_id": r["sample_id"]}
            for f in FOUNDATIONS:
                row[f] = float(np.mean([p[i] for i in FOUNDATION_ITEMS[f]]))
            rows.append(row)
    if not rows:
        raise SystemExit(f"No parsed records found in {RAW}. Run src/run_models.py first.")
    return pd.DataFrame(rows), pd.DataFrame(meta)


def load_human() -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    if not HUMAN.exists():
        raise SystemExit(f"{HUMAN} missing. Run src/load_human.py first.")
    h = pd.read_csv(HUMAN)
    return (h,
            h.groupby("country_label")[FOUNDATIONS].mean(),
            h.groupby("country_label")[FOUNDATIONS].std())


# --------------------------------------------------------------------------- #
# Metrics
# --------------------------------------------------------------------------- #

def parse_rates(meta: pd.DataFrame) -> pd.DataFrame:
    """Parse rate and retry rate per cell.

    Not a diagnostic but a finding: a model that cannot hold the response format
    in one language but can in another has told us something about that language.
    """
    g = meta.groupby(["model", "language", "persona"])
    out = g.agg(n=("parsed_ok", "size"),
                n_parsed=("parsed_ok", "sum"),
                mean_retries=("n_retries", "mean"),
                mean_seconds=("seconds", "mean")).reset_index()
    out["parse_rate"] = out["n_parsed"] / out["n"]
    out["pct_clean_json"] = g["extract_mode"].apply(lambda s: (s == "clean").mean()).values
    return out


def cell_means(scores: pd.DataFrame) -> pd.DataFrame:
    m = scores.groupby(["model", "language", "persona"])[FOUNDATIONS].agg(["mean", "std", "size"])
    m.columns = [f"{f}_{s}" for f, s in m.columns]
    return m.reset_index()


def distance_to_humans(scores: pd.DataFrame, hmean: pd.DataFrame) -> pd.DataFrame:
    """Metric 1. Mean absolute difference between the model's cell mean for a
    country persona and that country's human mean, per foundation:

        D(model, language, foundation)
            = (1/5) * sum_over_countries | model_mean(c) - human_mean(c) |

    Computed only over the five country personas (the no-persona cell has no
    country to compare against).
    """
    rows = []
    for (model, lang), g in scores[scores.persona != "none"].groupby(["model", "language"]):
        cm = g.groupby("persona")[FOUNDATIONS].mean()
        for f in FOUNDATIONS:
            diffs = [abs(cm.loc[c, f] - hmean.loc[c, f])
                     for c in SPANISH_COUNTRIES if c in cm.index]
            rows.append({"model": model, "language": lang, "foundation": f,
                         "mean_abs_diff": float(np.mean(diffs)),
                         "max_abs_diff": float(np.max(diffs))})
    return pd.DataFrame(rows)


def spread(scores: pd.DataFrame, hmean: pd.DataFrame) -> pd.DataFrame:
    """Metric 2a. Between-country differentiation: the SD (and range) of the five
    country means, for the model and for the humans. A model that flattens the
    personas has a spread near zero.
    """
    rows = []
    for (model, lang), g in scores[scores.persona != "none"].groupby(["model", "language"]):
        cm = g.groupby("persona")[FOUNDATIONS].mean().reindex(SPANISH_COUNTRIES)
        for f in FOUNDATIONS:
            rows.append({
                "model": model, "language": lang, "foundation": f,
                "model_spread_sd": float(cm[f].std()),
                "model_range": float(cm[f].max() - cm[f].min()),
                "human_spread_sd": float(hmean[f].std()),
                "human_range": float(hmean[f].max() - hmean[f].min()),
                "spread_ratio": float(cm[f].std() / hmean[f].std()),
            })
    return pd.DataFrame(rows)


def rank_correlation(scores: pd.DataFrame, hmean: pd.DataFrame) -> pd.DataFrame:
    """Metric 2b. Spearman rho between the model's and the humans' ordering of
    the five countries, per foundation.

    IMPORTANT: rho must always be read next to model_spread_sd from spread().
    When the five model means are nearly identical, rho is ranking noise and a
    high value means nothing. `spread_warning` flags that case.
    """
    rows = []
    for (model, lang), g in scores[scores.persona != "none"].groupby(["model", "language"]):
        cm = g.groupby("persona")[FOUNDATIONS].mean().reindex(SPANISH_COUNTRIES)
        for f in FOUNDATIONS:
            rho, p = stats.spearmanr(hmean.reindex(SPANISH_COUNTRIES)[f].values, cm[f].values)
            sd = float(cm[f].std())
            rows.append({"model": model, "language": lang, "foundation": f,
                         "spearman_rho": float(rho), "p_value": float(p),
                         "model_spread_sd": sd,
                         "spread_warning": "rho on near-identical means" if sd < 0.05 else ""})
    return pd.DataFrame(rows)


def persona_anova(scores: pd.DataFrame, human: pd.DataFrame) -> pd.DataFrame:
    """Metric 2c. One-way ANOVA of the persona (5 countries) on the model's
    scores, with eta-squared, alongside the same statistic for country in the
    human data:

        eta^2 = F*(k-1) / (F*(k-1) + (N-k))
    """
    def eta2(F, k, n):
        return float(F * (k - 1) / (F * (k - 1) + (n - k)))

    human_eta = {}
    for f in FOUNDATIONS:
        groups = [human[human.country_label == c][f].values for c in SPANISH_COUNTRIES]
        F, p = stats.f_oneway(*groups)
        human_eta[f] = (eta2(F, len(groups), len(human)), float(p))

    rows = []
    for (model, lang), g in scores[scores.persona != "none"].groupby(["model", "language"]):
        for f in FOUNDATIONS:
            groups = [g[g.persona == c][f].values for c in SPANISH_COUNTRIES]
            groups = [x for x in groups if len(x) > 1]
            F, p = stats.f_oneway(*groups)
            n = sum(len(x) for x in groups)
            he, hp = human_eta[f]
            rows.append({"model": model, "language": lang, "foundation": f,
                         "F": float(F), "p_value": float(p),
                         "eta2_model": eta2(F, len(groups), n),
                         "eta2_human": he, "p_human": hp})
    return pd.DataFrame(rows)


def sd_ratio(scores: pd.DataFrame, hsd: pd.DataFrame) -> pd.DataFrame:
    """Metric 3. Within-country flattening: the model's SD across its 50 samples
    for a country persona, divided by the human SD within that country.
    A ratio below 1 means the synthetic population is less varied than the real one.
    """
    rows = []
    for (model, lang, persona), g in scores[scores.persona != "none"].groupby(
            ["model", "language", "persona"]):
        if persona not in hsd.index:
            continue
        for f in FOUNDATIONS:
            ms, hs = float(g[f].std()), float(hsd.loc[persona, f])
            rows.append({"model": model, "language": lang, "country": persona,
                         "foundation": f, "model_sd": ms, "human_sd": hs,
                         "sd_ratio": ms / hs if hs else np.nan})
    return pd.DataFrame(rows)


def language_effect(scores: pd.DataFrame, human: pd.DataFrame) -> pd.DataFrame:
    """Metric 4. For the no-persona cells, the model's mean per language and its
    distance to the pooled human mean over the five Spanish-speaking countries.
    Answers: does asking in Spanish move the model toward these humans or away?
    """
    pooled = human[FOUNDATIONS].mean()
    rows = []
    for model, g in scores[scores.persona == "none"].groupby("model"):
        per_lang = g.groupby("language")[FOUNDATIONS].mean()
        for f in FOUNDATIONS:
            en = float(per_lang.loc["en", f]) if "en" in per_lang.index else np.nan
            es = float(per_lang.loc["es", f]) if "es" in per_lang.index else np.nan
            rows.append({"model": model, "foundation": f,
                         "en_mean": en, "es_mean": es, "en_minus_es": en - es,
                         "human_pooled_mean": float(pooled[f]),
                         "en_abs_dist": abs(en - pooled[f]),
                         "es_abs_dist": abs(es - pooled[f]),
                         "spanish_closer": bool(abs(es - pooled[f]) < abs(en - pooled[f]))})
    return pd.DataFrame(rows)


# --------------------------------------------------------------------------- #

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+")
    args = ap.parse_args()

    scores, meta = load_model_records(args.models)
    human, hmean, hsd = load_human()
    TABLES.mkdir(parents=True, exist_ok=True)

    # Loud warning if any cell is short. Running this mid-run silently produces
    # under-powered numbers that look perfectly normal, which is how a partial
    # result ends up in a paper.
    expected = json.loads((ROOT / "config.json").read_text())["samples_per_cell"]
    counts = meta.groupby(["model", "language", "persona"]).size()
    short = counts[counts < expected]
    if len(short):
        print("!" * 74)
        print(f"!! INCOMPLETE DATA: {len(short)} of {len(counts)} cells have fewer than "
              f"{expected} samples.")
        print("!! These tables are provisional. Re-run after the model runs finish.")
        for (mdl, lang, pers), n in short.items():
            print(f"!!   {mdl:<14} {lang} {pers:<10} {n}/{expected}")
        print("!" * 74 + "\n")

    outputs = {
        "model_scores.csv": scores,
        "parse_rates.csv": parse_rates(meta),
        "cell_means.csv": cell_means(scores),
        "distance_to_humans.csv": distance_to_humans(scores, hmean),
        "spread.csv": spread(scores, hmean),
        "rank_correlation.csv": rank_correlation(scores, hmean),
        "persona_anova.csv": persona_anova(scores, human),
        "sd_ratio.csv": sd_ratio(scores, hsd),
        "language_effect.csv": language_effect(scores, human),
    }
    for name, df in outputs.items():
        df.to_csv(TABLES / name, index=False)

    models = sorted(scores["model"].unique())
    print(f"models: {', '.join(models)}")
    print(f"administrations analysed: {len(scores)} "
          f"({len(meta) - len(scores)} unparseable excluded)\n")

    pr = outputs["parse_rates.csv"]
    worst = pr.nsmallest(3, "parse_rate")[["model", "language", "persona", "parse_rate"]]
    print("lowest parse rates:")
    print(worst.to_string(index=False) if (pr.parse_rate < 1).any()
          else "  all cells parsed at 100%")

    print("\nbetween-country spread (model SD / human SD; <1 = flatter than humans):")
    sp = outputs["spread.csv"].pivot_table(index="foundation", columns=["model", "language"],
                                           values="spread_ratio")
    print(sp.reindex(FOUNDATIONS).round(2).to_string())

    print("\npersona effect eta^2 (human eta^2 in the last column):")
    an = outputs["persona_anova.csv"]
    pv = an.pivot_table(index="foundation", columns=["model", "language"], values="eta2_model")
    pv["human"] = an.groupby("foundation")["eta2_human"].first()
    print(pv.reindex(FOUNDATIONS).round(3).to_string())

    print("\nwithin-country SD ratio (model/human, averaged over countries):")
    sr = outputs["sd_ratio.csv"].pivot_table(index="foundation", columns=["model", "language"],
                                             values="sd_ratio")
    print(sr.reindex(FOUNDATIONS).round(2).to_string())

    print(f"\nwrote {len(outputs)} tables -> {TABLES.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
