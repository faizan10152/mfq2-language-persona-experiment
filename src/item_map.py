"""Canonical MFQ-2 item mapping.

Maps the 36 final MFQ-2 item numbers (order of the official questionnaire,
as printed in Atari et al.'s official translation .docx files) onto the
column names of `Study_2_raw_dat.csv`.

PROVENANCE (all verified, nothing guessed):
  - The 50 item columns in Study_2_raw_dat.csv are the Study-2 administration
    of the item pool.  Atari et al. dropped 14 of them for cross-loadings in an
    ESEM (supplementary materials, "Study 2 / Exploratory Structural Equations
    Modeling"), leaving the 36 final items.
  - The six foundation scales below are copied verbatim from the authors' own
    analysis script `Code/Study 2/Code_Study2.R` on OSF (https://osf.io/srtxn/),
    lines defining CARE_tot ... PURITY_tot and the `model_6factors` CFA spec.
  - The 14 dropped columns are likewise copied from that script
    (the `align_dat` dplyr::select(-...) call).
  - Item-number -> column assignment was done by matching the English .docx
    wording against the Study-1a item pool in supplementary Table S1.  Three
    final items were reworded relative to the pool:
        16  "own community"   <- loyalty12 ("Everyone should love their own country.")
        28  "in their community" <- loyalty14 ("...in their country wins...")
        34  "strength of a sports team" <- loyalty6 ("strength of a family...")
    The R code confirms loyalty6/12/14 are the surviving Loyalty items and that
    `loyalty_new1` is NOT part of the MFQ-2 (it is dropped).  There is therefore
    no remaining A/B ambiguity in the Loyalty scale.
"""

# MFQ-2 item number (1..36) -> Study 2 CSV column
ITEM_TO_COLUMN = {
    1: "care12",              13: "care13",              25: "care14",
    2: "equality4",           14: "equality2",           26: "equalFairness10",
    3: "proportionality5",    15: "proportionality17",   27: "proportionality12",
    4: "loyalty5",            16: "loyalty12",           28: "loyalty14",
    5: "authority11",         17: "authority18",         29: "authority14",
    6: "purity3",             18: "purity17",            30: "purity9",
    7: "care11",              19: "care3",               31: "care1",
    8: "equality10",          20: "equalFairness6",      32: "equality6",
    9: "propFairness3",       21: "proportionality9",    33: "propFairness1",
    10: "loyalty16",          22: "loyalty13",           34: "loyalty6",
    11: "authority6",         23: "authority20",         35: "authority8",
    12: "purity2",            24: "purity13",            36: "purity6",
}

FOUNDATIONS = ["Care", "Equality", "Proportionality", "Loyalty", "Authority", "Purity"]

# Item numbers per foundation (every 6th item, MFQ-2 scoring key).
FOUNDATION_ITEMS = {
    "Care":            [1, 7, 13, 19, 25, 31],
    "Equality":        [2, 8, 14, 20, 26, 32],
    "Proportionality": [3, 9, 15, 21, 27, 33],
    "Loyalty":         [4, 10, 16, 22, 28, 34],
    "Authority":       [5, 11, 17, 23, 29, 35],
    "Purity":          [6, 12, 18, 24, 30, 36],
}

# Same thing expressed in CSV columns.  Verified identical to Code_Study2.R.
FOUNDATION_COLUMNS = {
    f: [ITEM_TO_COLUMN[i] for i in items] for f, items in FOUNDATION_ITEMS.items()
}

# Copied verbatim from Code_Study2.R (align_dat select(-...)); kept for the
# provenance check in check_human_data.py.
DROPPED_COLUMNS = [
    "care4", "care8",
    "equality11",
    "propFairness8", "propFairness9",
    "loyalty3", "loyalty8", "loyalty_new1",
    "authority1", "authority4", "authority17",
    "purity4", "purity7", "purity14",
]

# Attention-check pass criterion, from Code_Study2.R:
#   dplyr::filter(attention1 == 3 & attention2 == 5 & attention3 == 2)
ATTENTION_PASS = {"attention1": 3, "attention2": 5, "attention3": 2}

# Country label as spelled in the CSV -> label used in this project.
# NOTE: the CSV spells Colombia as "Columbia".
COUNTRY_SPELLING = {
    "Argentina": "Argentina",
    "Chile": "Chile",
    "Columbia": "Colombia",
    "Mexico": "Mexico",
    "Peru": "Peru",
}
SPANISH_COUNTRIES_CSV = list(COUNTRY_SPELLING.keys())
SPANISH_COUNTRIES = list(COUNTRY_SPELLING.values())
