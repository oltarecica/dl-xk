# Project Methodology Suggestions
## Kosovo Nightlights → Built-Up Surface Prediction

---

## Project Summary

Train a CNN to predict built-up surface fraction from nightlight satellite imagery patches over Kosovo. Systematic prediction errors (areas that are more built-up than the light suggests) are interpreted as spatial fingerprints of depopulation — validated against Kosovo's 2024 census.

---

## Methodology Stack

### 1. Data Pipeline — Lab 01 style

- Tile the Kosovo nightlights GeoTIFF (VIIRS) into 256×256 patches
- Pair each tile with the corresponding GHSL built-up fraction tile
- Filter blank / no-data patches (same logic as ETCI flood notebook)
- Handle resolution mismatch: VIIRS ~500m, GHSL available at 100m — decide on alignment strategy
- Analyze class distribution (built-up fraction histogram)

**Output:** Paired dataset of (nightlights patch, built-up fraction) tiles ready for training.

---

### 2. Baseline: OLS Regression on Pixel Statistics — `prediction_practice` style

- Extract mean and variance of nightlight intensity per tile
- Run OLS regression → built-up fraction
- Benchmark to beat
- Gives free coefficient interpretation: "1 unit increase in mean nightlight → X% increase in built-up fraction"

**Why include it:** Makes the CNN contribution legible. If CNN beats OLS, the spatial pattern learning is real.

---

### 3. Main Model: CNN Regression ⭐ — `convnet_solutions` style

Same architecture as the emotion classification notebook, with one change: swap the classification head for a single linear unit predicting a continuous built-up fraction.

```
Conv Block (8 filters) → MaxPool
Conv Block (16 filters) → MaxPool
Conv Block (32 filters) → MaxPool
Conv Block (64 filters) → MaxPool
GlobalAvgPool
Linear → scalar (built-up fraction)
```

- Loss: MSE
- Optimizer: AdamW
- The CNN captures spatial light gradients, spillover from roads, halos around city centers — patterns OLS on pixel means cannot see
- Input: nightlights patch (1 channel or RGB false-colour VV/VH composite if using SAR)
- Output: predicted built-up fraction per patch

---

### 4. Upgrade Option: U-Net Pixel-Level Regression — `segmentation_homework` style

Same U-Net architecture from the building footprint homework, but with a continuous regression output instead of binary segmentation.

- Input: 256×256 nightlights patch
- Output: 256×256 built-up fraction map (pixel-level)
- Loss: MSE per pixel
- Skip connections preserve fine spatial detail
- Produces a full residual map rather than one residual per patch — more visually compelling

**Worth attempting if time allows.** Stronger methodology section, richer maps.

---

### 5. Error Analysis — Lab 04 style

This is the core contribution of the project.

1. Compute per-tile residuals: `residual = actual built-up − predicted built-up`
2. Positive residuals = more built-up than light predicts → depopulation candidates
3. Aggregate residuals to municipality level
4. Rank municipalities by signed residual
5. Map spatially (overlay on Kosovo admin boundaries)
6. Validate against 2024 census population change figures

**Interpretation:**
- High positive residual = buildings exist, but nobody's home → vacancy, emigration
- Matches the spatial pattern of Kosovo's documented depopulation

---

## Recommended Stack

| Component | Approach | Notebook Reference |
|-----------|----------|--------------------|
| Data pipeline | Tiling, filtering, class distribution | Lab 01 |
| Baseline | OLS on pixel statistics | `prediction_practice` |
| Main model | CNN regression (patch → scalar) | `convnet_solutions` |
| Optional upgrade | U-Net pixel-level regression | `segmentation_homework` |
| Error analysis | Per-region residuals, spatial map | Lab 04 |

---

## Poster Structure (mapped to guidelines)

1. **Introduction** — Kosovo emigration context, why nightlights proxy development
2. **Research question** — Can CNN prediction errors in a nightlight → built-up model reveal spatial depopulation?
3. **Background literature** — VIIRS nightlights as economic proxy, GHSL built-up data, Kosovo demographic literature
4. **Data** — VIIRS nightlights, GHSL built-up surface, Kosovo 2024 census; tiling and alignment decisions
5. **Methodology** — OLS baseline, CNN regression, (optional U-Net); residual computation
6. **Results** — Model performance (MSE, R²), residual map, municipality-level correlation with census
7. **Future research** — Temporal analysis (multiple years), finer resolution, causal identification

---

## Key Decisions Still to Make

- **Prediction granularity**: patch-level scalar vs pixel-level map (U-Net)
- **Resolution alignment**: how to handle VIIRS 500m vs GHSL 100m mismatch
- **Census validation**: what specific variable from the 2024 census (population change, vacancy rate, household counts)?
- **Input channels**: single-channel nightlights only, or additional covariates (population density raster)?
