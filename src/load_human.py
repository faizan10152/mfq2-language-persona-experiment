"""Verification report + human MFQ-2 baselines from Atari et al. (2023) Study 2.

Run:  python src/load_human.py

Writes
  data/processed/human_respondents.csv   one row per respondent (5 Spanish-speaking
                                         countries), 36 items + 6 foundation scores
  data/processed/human_country_stats.csv per country x foundation: n, mean, sd
  data/processed/human_pooled_stats.csv  the 5 countries pooled, per foundation

and prints the checks required before any model runs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from item_map import (  # noqa: E402
    ATTENTION_PASS,
    COUNTRY_SPELLING,
    DROPPED_COLUMNS,
    FOUNDATION_COLUMNS,
    FOUNDATIONS,
    ITEM_TO_COLUMN,
    SPANISH_COUNTRIES_CSV,
)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "Study_2_raw_dat.csv"
OUT = ROOT / "data" / "processed"

META_COLS = [
    "age", "gender", "porient_1", "country",
    "attention1", "attention2", "attention3",
    "first_language", "religion", "religiosity_1", "education", "status",
]


def rule(title: str) -> None:
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")


def main() -> int:
    ok = True
    df = pd.read_csv(RAW)
    item_cols = [c for c in df.columns if c not in META_COLS]

    rule("1. File and item columns")
    print(f"rows: {len(df)}   columns: {df.shape[1]}")
    print(f"item columns in file: {len(item_cols)}")
    kept = set(ITEM_TO_COLUMN.values())
    dropped = set(DROPPED_COLUMNS)
    print(f"  MFQ-2 final items kept : {len(kept)}")
    print(f"  dropped by Atari et al.: {len(dropped)}")
    if kept | dropped != set(item_cols):
        print("  !! kept + dropped does not reconstruct the item columns")
        print(f"     unaccounted: {sorted(set(item_cols) - kept - dropped)}")
        print(f"     not in file: {sorted((kept | dropped) - set(item_cols))}")
        ok = False
    else:
        print("  OK: 36 kept + 14 dropped == all item columns in the file")
    if len(kept) != 36 or len(ITEM_TO_COLUMN) != 36:
        print("  !! item map is not 36 unique columns")
        ok = False

    rule("2. Attention checks")
    for c, v in ATTENTION_PASS.items():
        counts = df[c].value_counts(dropna=False).to_dict()
        print(f"  {c}: {counts}   (pass value = {v})")
    mask = pd.Series(True, index=df.index)
    for c, v in ATTENTION_PASS.items():
        mask &= df[c] == v
    print(f"  n before exclusion: {len(df)}")
    print(f"  n after  exclusion: {int(mask.sum())}   (excluded: {int((~mask).sum())})")
    if mask.all():
        print("  => the OSF file is ALREADY attention-filtered; the criterion from")
        print("     Code_Study2.R (attention1==3 & attention2==5 & attention3==2)")
        print("     removes nobody. Report n = n_before = n_after in the paper.")
    df = df[mask].copy()

    rule("3. Response scale and missingness (item columns)")
    vals = sorted(pd.unique(df[item_cols].values.ravel()))
    print(f"  unique item values: {vals}")
    if vals != [1, 2, 3, 4, 5]:
        print("  !! expected exactly 1..5")
        ok = False
    n_na = int(df[item_cols].isna().sum().sum())
    print(f"  missing item responses: {n_na}")
    if n_na:
        ok = False
    nonitem_na = df[META_COLS].isna().sum()
    nonitem_na = nonitem_na[nonitem_na > 0]
    print("  missing in metadata columns: "
          + (", ".join(f"{k}={v}" for k, v in nonitem_na.items()) if len(nonitem_na) else "none"))

    rule("4. Countries")
    vc = df["country"].value_counts()
    print(f"  {len(vc)} countries, n per country {vc.min()}-{vc.max()}")
    for csv_name, label in COUNTRY_SPELLING.items():
        n = int((df["country"] == csv_name).sum())
        note = "" if csv_name == label else f"   <-- spelled '{csv_name}' in the CSV, not '{label}'"
        print(f"  {label:<10} n = {n}{note}")
        if n == 0:
            ok = False

    sub = df[df["country"].isin(SPANISH_COUNTRIES_CSV)].copy()
    sub["country_label"] = sub["country"].map(COUNTRY_SPELLING)

    rule("5. first_language sanity check (5 Spanish-speaking countries)")
    norm = (sub["first_language"].astype(str).str.strip().str.lower()
            .str.normalize("NFKD").str.encode("ascii", "ignore").str.decode("ascii"))
    is_es = norm.str.contains("espa") | norm.str.contains("castell")
    for label, grp in sub.assign(is_es=is_es).groupby("country_label"):
        n, k = len(grp), int(grp["is_es"].sum())
        print(f"  {label:<10} Spanish/Castellano as first language: {k}/{n} ({k / n:.1%})")
    others = sub.loc[~is_es, "first_language"].value_counts()
    print(f"  non-Spanish self-reported first languages ({int((~is_es).sum())} respondents): "
          + ", ".join(f"{k!r}x{v}" for k, v in others.items()))
    print("  NOTE: these are free-text answers; typos ('Espanol', 'Espay') are counted as")
    print("  Spanish by the 'espa'/'castell' rule above. Respondents reporting Arabic or")
    print("  English are kept (Atari et al. did not exclude on first_language).")

    rule("6. Foundation scores (scoring key from Code_Study2.R)")
    for f in FOUNDATIONS:
        cols = FOUNDATION_COLUMNS[f]
        sub[f] = sub[cols].mean(axis=1)
        print(f"  {f:<16} = mean({', '.join(cols)})")

    OUT.mkdir(parents=True, exist_ok=True)
    keep_cols = ["country_label", "age", "gender", "porient_1", "first_language",
                 "religion", "religiosity_1", "education"] + list(ITEM_TO_COLUMN.values()) + FOUNDATIONS
    sub[keep_cols].to_csv(OUT / "human_respondents.csv", index=False)

    long = (sub.melt(id_vars="country_label", value_vars=FOUNDATIONS,
                     var_name="foundation", value_name="score")
            .groupby(["country_label", "foundation"])["score"]
            .agg(n="size", mean="mean", sd="std").reset_index())
    long["foundation"] = pd.Categorical(long["foundation"], FOUNDATIONS, ordered=True)
    long = long.sort_values(["foundation", "country_label"])
    long.to_csv(OUT / "human_country_stats.csv", index=False)

    pooled = (sub.melt(id_vars="country_label", value_vars=FOUNDATIONS,
                       var_name="foundation", value_name="score")
              .groupby("foundation")["score"].agg(n="size", mean="mean", sd="std").reset_index())
    pooled["foundation"] = pd.Categorical(pooled["foundation"], FOUNDATIONS, ordered=True)
    pooled.sort_values("foundation").to_csv(OUT / "human_pooled_stats.csv", index=False)

    rule("7. Human baselines (5 Spanish-speaking countries)")
    wide = long.pivot(index="country_label", columns="foundation", values="mean")[FOUNDATIONS]
    print("  means:\n" + wide.round(2).to_string())
    sdw = long.pivot(index="country_label", columns="foundation", values="sd")[FOUNDATIONS]
    print("\n  SDs:\n" + sdw.round(2).to_string())
    print("\n  between-country spread of the means (SD across the 5 countries):")
    print("  " + wide.std(axis=0).round(3).to_string().replace("\n", "\n  "))
    print(f"\n  n = {len(sub)} respondents")
    print(f"  wrote {(OUT / 'human_respondents.csv').relative_to(ROOT)}, "
          f"{(OUT / 'human_country_stats.csv').relative_to(ROOT)}, "
          f"{(OUT / 'human_pooled_stats.csv').relative_to(ROOT)}")

    print("\n" + ("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED - see !! above"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
