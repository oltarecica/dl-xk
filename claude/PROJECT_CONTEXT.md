# Project Context — Where the Lights Went Out

**DL in Image Processing — BSE 2025-26 | Olta Recica & Samuel Fraley**
**Deadline: June 27, 2026 23:59 | Max 1500 words**

---

## The Idea

Train a CNN to predict **GHSL built-up surface fraction** from **VIIRS nighttime lights patches** over Kosovo. Use the prediction residuals — places that are *more built-up than the light level predicts* — as a spatial fingerprint of depopulation. Validate against Kosovo's 2024 census.

**Why it works:** Buildings are permanent. When people emigrate, the lights go dark but the buildings stay. The CNN, trained on the normal relationship between light and built-up surface, sees darkness and says "not built up" — but the target says "buildings are there." That gap is the vacancy signal.

**Why Kosovo:** Kosovo had one of the world's sharpest population declines: 1,739,825 (2011) → 1,585,566 (2024), a −8.9% drop, driven by emigration primarily to Western Europe. The 2024 census is the first since 2011 and provides municipality-level ground truth.

---

## Data Pipeline (complete)

All data is in `data/`. Run order if you need to regenerate:

```bash
# 1. Export from GEE (only if re-downloading — already done)
#    Paste scripts/gee_export_script.js into code.earthengine.google.com

# 2. Reproject GHSL onto VIIRS pixel grid
.venv/bin/python scripts/align_rasters.py

# 3. Sanity check (saves data/sanity_check.png)
.venv/bin/python scripts/sanity-check.py

# 4. Clean census CSV
.venv/bin/python scripts/prepare_census.py
```

### Raster files

| File | Role | Details |
|---|---|---|
| `viirs_nightlights_kosovo_2025.tif` | **CNN input** | VIIRS annual median 2025, 500m, EPSG:4326, shape (336, 402) |
| `ghsl_builtup_kosovo_2020_aligned.tif` | **CNN target** | GHSL built-up fraction 2020 (real satellite obs, last available), aligned to VIIRS grid |
| `ghsl_population_kosovo_2020_aligned.tif` | Pixel-level population | GHS-POP 2020, aligned to VIIRS grid, useful for per-pixel weighting |

Both GHSL files come from `JRC/GHSL/P2023A`. The 2025 epoch in that collection is a model projection — **do not use it as CNN target**. The 5-year gap between 2020 structures and 2025 lights is intentional and is the signal.

### Why 92% zeros in GHSL is fine

Kosovo is mostly mountains, forests, and farmland. At 500m resolution, most pixels have no built-up surface. This is expected, not a data quality issue. When evaluating the model, report metrics on **all pixels** and separately on **non-zero pixels**.

### Census data

| File | Contents |
|---|---|
| `census24_05_20260620-155843.csv` | Raw download from askdata.rks-gov.net (population by ethnicity, sex, municipality, 2011 & 2024) |
| `kosovo_census_clean.csv` | Clean version: 38 municipalities, pop_2011, pop_2024, pop_change_pct |

**4 northern municipalities** (Leposaviq, Mitrovica e Veriut, Zubin Potok, Zveçan) have `NaN` for 2011 — the Serb community boycotted both censuses, so figures are not comparable. Exclude them from validation.

**Suburban Prishtina growth** (Fushe Kosove +84%, Graçanicë +73%, Partesh +81%) reflects urbanization, not depopulation. Expect the model to show low positive residuals or negative residuals there (new buildings being built faster than lights predict).

### Admin shapefiles

`data/whosonfirst-data-admin-xk-latest/` — Kosovo boundaries in EPSG:4326.

Key layers:
- `*-localadmin-polygon.shp` — 40 rows, but Kosovo has 38 municipalities. The 40 include duplicate entries (Fushe Kosova/Fushe Kosovo, two Kamenice, two Prishtine). **Deduplicate before spatial joining.**
- `*-region-polygon.shp` — 7 regions (coarser)

---

## Methodology Plan

This maps directly to the class notebooks.

### Step 1 — Data loading & tiling
Reference: `class_notebooks/spatial_image_solutions.ipynb` + `Lab_01_data_preparation.ipynb`

- Read both aligned TIFs with rasterio
- Tile into patches (suggest ~32×32 pixels at 500m = ~16km × 16km windows, or smaller)
- Filter blank tiles (tiles where GHSL target is all zeros — these add no signal)
- Split into train/val/test by spatial region (not random — avoid spatial leakage)

### Step 2 — OLS baseline
Reference: `class_notebooks/prediction_practice.ipynb`

Simple linear regression: mean VIIRS radiance per patch → mean built-up fraction. This is the benchmark the CNN must beat.

### Step 3 — CNN regression
Reference: `class_notebooks/convnet_solutions.ipynb`

The `SimpleConvNet` in that notebook is a 4-block CNN (8/16/32/64 filters) with GlobalAvgPool and a softmax head for classification. To adapt to regression:
- Change final layer: `nn.Linear(64, 1)` (no activation)
- Change loss: `nn.MSELoss()`
- The rest is identical

Output: predicted built-up fraction per patch.

### Step 4 — Residual analysis
Reference: `class_notebooks/lab-04-error-analysi.ipynb`

```python
residual = ghsl_actual - cnn_predicted
```

Positive residual → more buildings than light predicts → depopulation signal.

- Map residuals spatially (imshow over Kosovo)
- Aggregate mean residual per municipality (spatial join with shapefile)
- Correlate municipality mean residual with `pop_change_pct` from census
- Expected: municipalities with most population loss have highest positive residuals

### Optional Step 5 — U-Net
Reference: `class_notebooks/segmentation_homework.ipynb`

Olta already completed this homework. The U-Net gives a **pixel-level prediction map** rather than a patch-level scalar, which produces a finer residual map. Adapt by changing the output head to 1 channel + no sigmoid (or sigmoid if you want a fraction in [0,1]).

---

## Key Things to Keep in Mind

1. **No data augmentation with flips** — spatial orientation matters for satellite imagery (north is up). Rotation by 90° is borderline. Safest: no geometric augmentation, only brightness/contrast jitter on VIIRS.

2. **Spatial train/val/test split** — do NOT split randomly. Random splits leak spatial autocorrelation and inflate validation metrics. Split by geographic region (e.g. NW/NE/S thirds of Kosovo).

3. **Evaluate on non-zero pixels separately** — the 92% zeros make MAE look artificially good. Always report a second metric computed only on pixels where GHSL > 0.

4. **Northern municipalities** — Leposaviq, Mitrovica e Veriut, Zubin Potok, Zveçan had census boycotts. Drop these from the validation scatter plot and note it explicitly in the poster.

5. **GHSL 2025 is a projection, not observation** — The P2023A collection has a 2025 epoch but it's modeled, not satellite-derived. We deliberately use 2020 as the target.

6. **Cite the data sources in the poster:**
   - VIIRS: NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG (via GEE)
   - GHSL: JRC/GHSL/P2023A/GHS_BUILT_S (Pesaresi et al. 2024)
   - GHS-POP: JRC/GHSL/P2023A/GHS_POP
   - Census: Kosovo Agency of Statistics (ASK), Census 2024, askdata.rks-gov.net

---

## Class Notebook Map

| Notebook | Topic | Project relevance |
|---|---|---|
| `Lab_01_data_preparation.ipynb` | SAR tiling, blank filtering, class balance | Data pipeline pattern |
| `convnet_solutions.ipynb` | 4-block CNN for classification | **Main CNN template** — swap head to regression |
| `segmentation_homework.ipynb` | U-Net (Olta's completed HW) | Optional U-Net upgrade |
| `lab-02-model-training.ipynb` | Siamese U-Net, transfer learning | Pretrained encoder reference |
| `vision_transformer_solutions.ipynb` | ViT regression | Regression output pattern |
| `lab-04-error-analysi.ipynb` | Per-tile/region error analysis | **Error analysis template** |
| `spatial_image_solutions.ipynb` | rasterio, GeoTIFF, spatial prediction | **Data loading template** |
| `prediction_practice.ipynb` | OLS baseline style | Baseline benchmark |
| `lab-03-impact-analysisy.ipynb` | Impact analysis | Context |

---

## Literature (full review in `claude/literature_review.md`)

- Henderson et al. 2012 AER — foundational NTL as economic proxy
- Jean et al. 2016 Science — CNN + NTL for poverty mapping (closest methodological ancestor)
- Yeh et al. 2020 Nature Comms — CNN on satellite for economic wellbeing
- Pesaresi et al. 2024 — GHSL built-up surface dataset paper
- NTL & population changes in Europe, 2015 Ambio — validates the residual logic directly

---

## What's Left to Do

- [ ] Modelling notebook (data loading, tiling, OLS baseline, CNN, residual map)
- [ ] Poster draft (1500 words max, see `assessment_guidelines.md`)
- [ ] Consider U-Net upgrade if time allows
