"""
Clean the raw ASK census CSV into a per-municipality population table.
Input:  data/census24_05_20260620-155843.csv  (downloaded from askdata.rks-gov.net)
Output: data/kosovo_census_clean.csv
"""

import re
import unicodedata
import pandas as pd

RAW = "data/census24_05_20260620-155843.csv"
OUT = "data/kosovo_census_clean.csv"

# --- load, skip the title row in row 0 ---
df = pd.read_csv(RAW, skiprows=1)

# keep only "Total" sex rows, drop the country-level row
df = df[df["Sex"] == "Total"]
df = df[df["Municipality"] != "KOSOVA"].copy()

# rename the columns we need
df = df.rename(columns={
    "Municipality":  "municipality_alb",
    "2011 Total":    "pop_2011",
    "2024 Total":    "pop_2024",
})

df = df[["municipality_alb", "pop_2011", "pop_2024"]].copy()

# ":" means data not available (northern municipalities boycotted 2011 census)
df["pop_2011"] = pd.to_numeric(df["pop_2011"], errors="coerce")
df["pop_2024"] = pd.to_numeric(df["pop_2024"], errors="coerce")

# compute % change only where both years are available
df["pop_change_pct"] = ((df["pop_2024"] - df["pop_2011"]) / df["pop_2011"] * 100).round(2)

# ASCII-normalize municipality names for joining against shapefiles
def to_ascii(s):
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")  # strip diacritics
    return s.strip()

df["municipality"] = df["municipality_alb"].apply(to_ascii)

# manual fixes for names that differ from the shapefile
name_map = {
    "Mitrovice":           "Mitrovice e Jugut",   # south Mitrovica (keep distinct)
    "Mitrovice e Veriut":  "Mitrovica e Veriut",  # north Mitrovica
    "Fush Kosov":          "Fushe Kosove",
    "Novoberd":            "Novo Berde",
    "Shterpce":            "Shterpc",
}
df["municipality"] = df["municipality"].replace(name_map)

df = df[["municipality", "municipality_alb", "pop_2011", "pop_2024", "pop_change_pct"]]
df = df.sort_values("municipality").reset_index(drop=True)

df.to_csv(OUT, index=False)

print(f"Saved {len(df)} municipalities to {OUT}")
print()
print(df.to_string(index=False))
print()

# flag municipalities missing 2011 data
missing = df[df["pop_2011"].isna()]
if not missing.empty:
    print(f"\nWARNING: {len(missing)} municipalities missing 2011 data (census boycott):")
    for m in missing["municipality"]:
        print(f"  {m}")
    print("These will be excluded from residual-vs-change validation.")
