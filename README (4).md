# Balkans Nightlight Transfer Learning — Complete Pipeline

## Project Overview

**Research Question:** Do satellite-derived built-environment features generalize across Balkan countries in predicting settlement-level economic underperformance (measured by nightlight change)?

**Approach:** Leave-One-Country-Out (LOOCV) transfer learning using a 4-layer CNN on temporal satellite data.

**Countries:** Serbia, Kosovo, Albania, North Macedonia, Montenegro, Bosnia and Herzegovina

---

## Files You Need

### 1. Raw Satellite Data (Google Drive)

All files are stored in your **Google Drive** under `MyDrive/balkans_temporal/` and `MyDrive/balkans_ancillary/`:

#### Temporal Data (VIIRS Nightlights 2013-2017)
```
balkans_temporal/
├── balkans_Serbia_VIIRS_temporal.tif
├── balkans_Kosovo_VIIRS_temporal.tif
├── balkans_Albania_VIIRS_temporal.tif
├── balkans_North_Macedonia_VIIRS_temporal.tif
├── balkans_Montenegro_VIIRS_temporal.tif
└── balkans_Bosnia_and_Herzegovina_VIIRS_temporal.tif
```
- **Source:** Google Earth Engine (NOAA/VIIRS/DNB/ANNUAL_V21)
- **Resolution:** 500m
- **Content:** 5 bands (one per year: 2013, 2014, 2015, 2016, 2017)
- **Extraction:** See "Data Extraction" section below

#### Ancillary Data (Land Cover + Population)
```
balkans_ancillary/
├── balkans_Serbia_ESA_WorldCover_50m.tif
├── balkans_Serbia_GHSL_Pop.tif
├── balkans_Kosovo_ESA_WorldCover_50m.tif
├── balkans_Kosovo_GHSL_Pop.tif
├── ... (one pair per country)
```
- **Land Cover (ESA WorldCover):** 50m resolution, 11 classes (class 50 = built-up)
- **Population (GHSL):** 100m resolution, people/pixel counts

---

### 2. Python Scripts (Local or GitHub)

You have one main Colab notebook with cells:

#### Cell 0 — Setup
```python
import ee
import pandas as pd
import folium
from datetime import datetime

ee.Authenticate()
ee.Initialize(project='YOUR_GCP_PROJECT')

DATASETS = {"country_boundaries": "USDOS/LSIB_SIMPLE/2017"}
COUNTRIES = {
    "Serbia": [18.8, 42.2, 22.9, 46.2],
    "Kosovo": [20.0, 41.8, 21.8, 43.3],
    # ... etc
}
```

#### Cell 1 — Load Actual Country Boundaries
Uses USDOS/LSIB dataset to get real country polygons (not bounding boxes).

#### Cells 2-4 — Extract Data from GEE
- Exports VIIRS temporal (all 6 countries)
- Exports ESA WorldCover (all 6 countries)
- Exports GHSL Population (all 6 countries)
- Each runs in parallel, takes ~30-40 min total

#### Cells 5+ — Local Processing (Python, Colab GPU)
```python
colab_full_pipeline.py  # Main training script
```

**What it does:**
1. Loads .tif files from Drive
2. Extracts 64×64 patches on regular grid (stride=32)
3. Stacks 7 features: VIIRS 2013-2017 (5) + built-up (1) + population (1)
4. Trains CNN with LOOCV (6 folds, one per country)
5. Evaluates: Accuracy, F1, AUC per fold
6. Visualizes: Confusion matrices, prediction maps

---

## How to Use — Step by Step

### Step 1: Authenticate Google Earth Engine

In Colab:
```python
import ee
ee.Authenticate()  # Opens browser for login
ee.Initialize(project='YOUR_GCP_PROJECT')
```

### Step 2: Mount Google Drive

In Colab:
```python
from google.colab import drive
drive.mount('/content/drive')
```

### Step 3: Run Data Extraction (one-time)

**In Google Earth Engine or Colab:**

Use the cells that export VIIRS, WorldCover, Population to Drive folders:
- `balkans_temporal/`
- `balkans_ancillary/`

**Takes:** ~30-40 minutes (runs in parallel on GEE servers)

### Step 4: Run Full Pipeline

Paste `colab_full_pipeline.py` into Colab cell, run once:

```python
# COLAB CELL — Complete Pipeline
import numpy as np
import rasterio
from pathlib import Path
# ... (paste entire script)
```

**What happens:**
1. Loads 2141 patches from Drive (10 sec)
2. Extracts patches on grid (5 sec)
3. Runs LOOCV training (6 folds × ~1 min each = ~6 min on GPU)
4. Prints results:
   ```
   --- Fold: Test on Serbia ---
     Train samples: 1301
     Test samples: 840
     Accuracy: 0.429
     F1 (weighted): 0.375
     AUC (weighted): 0.677
   ```

**Total runtime:** ~20 seconds on GPU

### Step 5: Visualize Results

Run visualization cells:
```python
# Confusion matrices
# Prediction confidence distributions
# Full-country prediction maps
# Error analysis
```

---

## Data Structure

### Input Tensor Format

Each patch is a **7-channel image** at **64×64 pixels**:

```
Channels:
  0: VIIRS 2013 nightlights (500m)
  1: VIIRS 2014 nightlights
  2: VIIRS 2015 nightlights
  3: VIIRS 2016 nightlights
  4: VIIRS 2017 nightlights
  5: Built-up binary (1 if ESA class 50, else 0)
  6: Population log-transformed (log1p of people/pixel)

Shape per patch: (7, 64, 64) = 28,672 values
```

### Labels (Target Variable)

**3-class classification:**
- **Class 0:** Low growth (bottom tercile of nightlight change 2013→2017)
- **Class 1:** Medium growth (middle tercile)
- **Class 2:** High growth (top tercile)

Computed per-country to ensure balance:
```python
pct_change = (viirs_2017 - viirs_2013) / (viirs_2013 + 1e-6) * 100
labels = np.digitize(pct_change, [np.percentile(pct_change, [33, 67])])
```

---

## Model Architecture

```
Input: (7, 64, 64)
  ↓
Conv Block 1: 7 → 32 filters, MaxPool 2×2 (64 → 32)
  ↓
Conv Block 2: 32 → 64 filters, MaxPool 2×2 (32 → 16)
  ↓
Conv Block 3: 64 → 128 filters, MaxPool 2×2 (16 → 8)
  ↓
Conv Block 4: 128 → 256 filters, MaxPool 2×2 (8 → 4)
  ↓
Flatten: 256 × 4 × 4 = 4096
  ↓
Dense: 4096 → 512 (ReLU + Dropout 0.4)
  ↓
Output: 512 → 3 (classes)
```

**Training:**
- Optimizer: Adam (lr=1e-3, weight_decay=1e-4)
- Loss: CrossEntropyLoss
- Epochs: 50
- Batch size: 32
- Scheduler: StepLR (drop lr at epochs 20, 40)

---

## How to Share with Your Partner

### Option 1: Shared Google Drive Folder (Recommended)

1. **Create folder** `MyDrive/balkans_project_shared/`
2. **Add files:**
   - Raw data: `balkans_temporal/` + `balkans_ancillary/` (link or copy)
   - Code: `colab_full_pipeline.py` (save as text file)
   - Results: `loocv_results.csv` (export after running)
   - This README: `README.md`

3. **Share link** with partner (Viewer access is fine)

4. **Partner runs:**
   - Open Colab
   - Mount shared Drive
   - Run pipeline (all data is there)

### Option 2: GitHub Repository

1. Create repo: `balkans-nightlight-transfer-learning`

2. Add files:
   ```
   repos/
   ├── README.md (this file)
   ├── colab_full_pipeline.py
   ├── data_extraction_gee.py (GEE export cells)
   ├── results/
   │   ├── loocv_results.csv
   │   └── confusion_matrices.png
   └── docs/
       └── methodology.md
   ```

3. **Push to GitHub**, share link

4. **Partner clones**, links to Drive data, runs pipeline

### Option 3: Colab Notebook (Easiest)

1. Create Colab notebook: `Balkans_Nightlight_Transfer_Learning`
2. Add cells in order:
   - Cell 0: Setup + imports
   - Cell 1: Load boundaries
   - Cells 2-4: Extract data (skip if already done)
   - Cell 5: Full pipeline
   - Cell 6-8: Visualizations
3. Share notebook link (Colab handles permissions)
4. Partner opens, runs cells sequentially

---

## Results Summary

**Current Performance (LOOCV):**

| Country | Accuracy | F1 | AUC |
|---------|----------|----|----|
| Serbia | 0.430 | 0.375 | 0.677 |
| Kosovo | 0.385 | 0.325 | 0.722 |
| Albania | 0.491 | 0.475 | 0.727 |
| N. Macedonia | 0.505 | 0.490 | 0.683 |
| Montenegro | 0.506 | 0.470 | 0.704 |
| Bosnia & Herz. | 0.519 | 0.518 | 0.711 |

**Interpretation:**
- Random baseline = 33% (3 classes)
- Model achieves 43-52% (10-19 points above baseline)
- AUC ~0.71 indicates moderate signal
- **Best transfer:** Bosnia (more urbanized?)
- **Worst transfer:** Kosovo (smallest, different development)

---

## Troubleshooting

### "File not found" error
- Check Drive folders exist: `/content/drive/MyDrive/balkans_temporal/`
- Use `!ls /content/drive/MyDrive/` in Colab to list files

### Out of memory
- Reduce patch stride (e.g., stride=64 instead of 32)
- Reduce batch size in training (e.g., batch_size=16)

### Low accuracy
- Check that all 5 VIIRS years are loading (shape should be (5, H, W))
- Verify labels are 3-class (values 0, 1, 2)
- Increase epochs (try 100 instead of 50)

### GPU not available
- In Colab: Runtime → Change runtime type → GPU
- Falls back to CPU automatically (slower)

---

## Files Checklist for Partner

Before sharing, ensure partner has:
- [ ] Access to Drive folder with all .tif files
- [ ] This README.md
- [ ] colab_full_pipeline.py (or link to notebook)
- [ ] Instructions on how to authenticate GEE
- [ ] Expected runtime (~20 sec on GPU)
- [ ] Sample output (loocv_results.csv)

---

## Questions?

- **Data source issues:** Check GEE collection names in script
- **Model performance:** Adjust hyperparameters in `train_fold()` function
- **Visualization issues:** Ensure matplotlib is imported, check figure sizes
- **Drive access:** Verify folder sharing permissions

Good luck with your project! 🚀
