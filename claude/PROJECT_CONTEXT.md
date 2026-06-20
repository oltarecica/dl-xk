# Project Context — Where the Lights Went Out

**DL in Image Processing — BSE 2025-26 | Olta Recica & Samuel Fraley**
**Deadline: June 27, 2026 23:59 | Max 1500 words**
**Notebook: `nightlights_residuals.ipynb`**

---

## The Idea

Train a CNN to predict **GHSL 2015 built-up surface fraction** from **VIIRS 2025 nighttime lights patches** over Kosovo. Use prediction residuals — places that are *more built-up than the light level predicts* — as a spatial fingerprint of depopulation. Validate against Kosovo's 2024 census at municipality level.

**Why GHSL 2015, not 2020:** Kosovo's main emigration wave peaked 2015-2020. Using GHSL 2020 means both the buildings AND the lights already reflect the post-emigration state — no temporal lag to exploit. GHSL 2015 captures the built environment BEFORE people left. VIIRS 2025 captures lights AFTER. The residual captures buildings that exist but no longer have matching economic activity.

**Why Kosovo:** −8.9% population decline 2011-2024, one of the sharpest in the world. 2024 census provides fresh municipality-level ground truth.

---

## Files (all in `data/`)

| File | Role |
|---|---|
| `viirs_nightlights_kosovo_2025.tif` | CNN input — VIIRS annual median 2025, 500m, EPSG:4326, shape (336, 402) |
| `ghsl_builtup_kosovo_2015.tif` | Raw GHSL 2015 from GEE |
| `ghsl_builtup_kosovo_2015_aligned.tif` | CNN target — GHSL 2015 reprojected to VIIRS grid |
| `kosovo_census_clean.csv` | 38 municipalities, pop_2011, pop_2024, pop_change_pct |
| `census24_05_20260620-155843.csv` | Raw census download from ASK |
| `nightlights_municipalities.csv` | Mean NTL per municipality for 2014, 2019, 2025 |
| `whosonfirst-data-admin-xk-latest/` | Kosovo admin shapefiles |

**Scripts:**
- `scripts/align_rasters.py` — reprojects GHSL onto VIIRS pixel grid
- `scripts/prepare_census.py` — cleans raw census CSV
- `scripts/gee_export_script.js` — GEE export script (VIIRS 2025 + GHSL 2015)

---

## What We Tried and What Happened

### First attempt: GHSL 2020 + VIIRS 2025
Census validation gave r=+0.435, p=0.010 — positive, opposite of hypothesis. Root cause: by 2020, both GHSL and VIIRS already reflected the post-emigration state. No temporal lag, no signal. Serb-minority municipalities (dense traditional housing, low commercial lighting) drove the positive correlation.

Sensitivity analyses: Albanian-majority only (r=-0.155, ns), depopulating only (r=-0.100, ns), drop Fushe Kosove (r=-0.118, ns). All insignificant.

### Fix: switch to GHSL 2015
Re-exported GHSL 2015 from GEE, re-ran alignment, retrained CNN. Results:
- Full sample: r=+0.005, p=0.979 (flat — ethnic confounder neutralized)
- Albanian-majority only: r=-0.381, p=0.050 (right direction, borderline significant)
- Albanian-majority + drop Fushe Kosove: r=-0.260, p=0.199 (worse — Fushe Kosove was helping the trend)

**Best result: Albanian-majority, r=-0.381, p=0.050.**

### Deforestation tangent (abandoned)
Explored U-Net on Sentinel-2 to detect Kosovo forest loss. Downloaded data, ran EDA. Found 77:1 class imbalance (Hansen only captures clear-cutting, not Kosovo's selective illegal logging). Abandoned and returned to depopulation project.

---

## Bugs Fixed

| Bug | Fix |
|---|---|
| MPS device error (weight type mismatch) | Added `model = model.to(device)` before training |
| `y` tensor overwritten in training loop | Renamed to `y_full` |
| Residual map bleeding outside Kosovo | Rasterized municipality outline as mask with `rasterio.features.rasterize` |
| Blurry residual map | Added `interpolation='nearest'` and larger figure |
| Kamenice missing from spatial join | Dissolved duplicate shapefile polygons instead of dropping |
| Name mismatches shapefile/census | Built `shp_to_census` mapping dict |
| VIIRS normalization bug | Clipped at 99th percentile (19.354) instead of raw max (146) — fixed R² from 0.87 to 0.92 |

---

## Current Results

| Model | MSE | R² |
|---|---|---|
| OLS baseline | 0.000022 | 0.7593 |
| CNN (SimpleConvNet) | 0.000007 | 0.9223 |

**Census validation:**
- Full sample (38 municipalities): r=+0.005, p=0.979
- Albanian-majority only (28 municipalities): r=−0.381, p=0.050

**Residuals:** 409 positive (more built-up than lights predict), 1424 negative.

---

## Key Design Decisions

- **VIIRS normalization:** clip at 99th percentile (19.354), divide by `viirs_clip`. Raw max=146 was compressing 99% of pixels into [0, 0.13].
- **Patches:** 32×32, stride 8, 1833 total. All patches kept including zeros (teach model that dark = not built-up).
- **Split:** 70/15/15 random, seed=28.
- **Early stopping:** patience=10, best model saved to `best_model.pth` (stopped at epoch 48).
- **Shapefile dedup:** 40 rows → 38 real municipalities. Dissolved duplicates (Kamenice, Prishtine, Fushe Kosova/Kosovo).
- **4 northern municipalities excluded from census validation:** Leposaviq, Mitrovica e Veriut, Zubin Potok, Zveçan — boycotted both 2011 and 2024 censuses, figures not comparable.

---

## Shapefile Name Mapping

```python
shp_to_census = {
    'DeCan': 'Decan', 'Fushe Kosova': 'Fushe Kosove', 'Gllogovc': 'Gllogoc',
    'GraCanica': 'Gracanice', 'Hani I Elezit': 'Hani i Elezit',
    'KaCanik': 'Kacanik', 'Mamusha': 'Mamushe', 'Mitrovice': 'Mitrovice e Jugut',
    'Novo Berdo': 'Novoberde', 'Shte Rpce': 'Shterpc', 'ZveCan': 'Zveqan',
}
```

---

## What's Left

- [ ] Fix stale observation cells in notebook (CNN eval says 0.87, residuals says 585, histogram says right-skewed)
- [ ] Write census validation observation cell (main finding)
- [ ] Poster draft (1500 words max)

---

## Literature

- Henderson et al. 2012 AER — foundational NTL as economic proxy
- Jean et al. 2016 Science — CNN + NTL for poverty mapping (closest methodological ancestor)
- Yeh et al. 2020 Nature Comms — CNN on satellite for economic wellbeing
- Pesaresi et al. 2024 — GHSL built-up surface dataset
- NTL & population changes in Europe 2015 Ambio — validates the residual logic
