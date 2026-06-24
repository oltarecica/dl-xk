# dl-xk

Current working pipeline for the Balkans nightlights transfer-learning project.

This README reflects the decisions currently implemented in [eda_v2.ipynb](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/eda_v2.ipynb) and [model_v2.ipynb](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/model_v2.ipynb).

## Project Goal

Predict patch-level nightlight change patterns across Balkan countries using multi-channel satellite/context data, then evaluate cross-country transfer with leave-one-country-out validation.

Countries:

- Albania
- Bosnia and Herzegovina
- Kosovo
- Montenegro
- North Macedonia
- Serbia

## Locked-In Decisions

These are the current default choices and should be treated as the main pipeline unless we explicitly decide to run a sensitivity analysis.

### Dataset version

Use the `v4` raster stack:

- file pattern: `data/gee/balkans_{country}_v4.tif`
- loaded by `load_country()` in `eda_v2.ipynb`

Do not use `v3` for the main run anymore.

### Raster channels in `v4`

Band order:

0. `viirs_2013`
1. `viirs_2014`
2. `viirs_2015`
3. `viirs_2016`
4. `builtup_fraction`
5. `population`
6. `elevation`
7. `slope`
8. `infra_proximity`
9. `smod_code`
10. `viirs_2017`

Notes:

- `viirs_2017` is the target band and must not be used as a model input.
- `smod_code` is included as a feature channel, not as the default sampling mask.

### Patch geometry

Main modeling scale:

- `PATCH_SIZE = 32`
- `STRIDE = 16`

Rationale:

- `8x8` is much denser but likely too local/noisy.
- `64x64` is much coarser and reduces sample size too much in smaller countries.
- `32x32` is the current compromise between spatial context and usable sample size.

### Patch retention rule

Use the endpoint-based blank filter, not the baseline-only 2013 filter.

Current rule:

1. Drop patches with too much missingness in the `viirs_2017` patch:
   - `np.isnan(v17_patch).mean() > NAN_THRESH`
2. Keep a patch only if:
   - `np.nanmean(np.maximum(viirs_2013_patch, viirs_2017_patch)) >= BLANK_THRESH`

Current threshold:

- `BLANK_THRESH = 0.3`

Interpretation:

- this is an endpoint-based inclusion rule
- it is not classic feature leakage because `viirs_2017` is not a model input
- it does condition sample inclusion on the target endpoint, so it should be described honestly in the writeup

### Why we kept the endpoint filter

We tested a stricter baseline-only filter using `viirs_2013` alone.

Patch count changes under baseline-only filtering:

| Country | Endpoint Filter | Baseline-Only Filter | Delta | Percent Change |
| --- | ---: | ---: | ---: | ---: |
| Albania | 459 | 262 | -197 | -42.9% |
| Bosnia and Herzegovina | 959 | 562 | -397 | -41.4% |
| Kosovo | 230 | 200 | -30 | -13.0% |
| Montenegro | 220 | 126 | -94 | -42.7% |
| North Macedonia | 444 | 273 | -171 | -38.5% |
| Serbia | 1652 | 1310 | -342 | -20.7% |

Decision:

- keep the endpoint-based filter as the main pipeline
- treat baseline-only filtering as a sensitivity check, not the default workflow

### Target variables

Patch extraction currently creates two target definitions.

#### 1. `logratio`

Computed from 2013 and 2017 VIIRS:

`log_ratio = np.log1p(viirs_2017) - np.log1p(viirs_2013)`

This replaced the old percent-change target.

#### 2. `momentum`

Computed as departure from the extrapolated 2013-2016 trend:

- take patch means for VIIRS 2013, 2014, 2015, 2016
- transform with `log1p`
- fit a linear trend across the four years
- predict 2017 from that trend
- subtract predicted 2017 from actual 2017 in log space

#### Labels

For both targets:

- patch-level scalar values are computed
- terciles are defined per country using the 33rd and 67th percentiles
- labels are assigned with `np.digitize()`

Main recommendation:

- run `logratio` first as the primary target
- run `momentum` as the secondary comparison

## Input Tensor Used By The Model

The patch arrays saved by `eda_v2.ipynb` include all channels, including the target band.

In `model_v2.ipynb`, the model input channels are:

`INPUT_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`

So the CNN uses:

- VIIRS 2013
- VIIRS 2014
- VIIRS 2015
- VIIRS 2016
- built-up fraction
- population
- elevation
- slope
- infrastructure proximity
- SMOD code

The CNN excludes:

- `viirs_2017` at channel 10

## Saved Patch Files

Expected outputs from `eda_v2.ipynb`:

- `data/patches_v2_32x32/{country}_patches.npy`
- `data/patches_v2_32x32/{country}_labels_logratio.npy`
- `data/patches_v2_32x32/{country}_labels_momentum.npy`

Equivalent folders can exist for other patch sizes, for example:

- `data/patches_v2_8x8/`
- `data/patches_v2_64x64/`

## Notebook Roles

### `eda_v2.ipynb`

This notebook is the source of truth for:

- loading the `v4` stack
- patch extraction
- patch filtering
- target computation
- saving patch tensors and label arrays
- visual diagnostics and sensitivity checks

### `model_v2.ipynb`

This notebook is the source of truth for:

- loading saved patch tensors
- selecting the target with `TARGET = "logratio"` or `TARGET = "momentum"`
- leave-one-country-out modeling
- performance evaluation
- saving results to:
  - `data/loocv_results_v2_{TARGET}.pkl`

## Recommended Run Order

If someone new is picking this up, use this order:

1. Open `eda_v2.ipynb`.
2. Confirm `load_country()` is reading `balkans_{country}_v4.tif`.
3. Run the notebook from the top through patch extraction and save cells.
4. Save fresh patch files for the patch size you want, usually `32x32`.
5. Open `model_v2.ipynb`.
6. Set:
   - `PATCH_SIZE = 32`
   - `TARGET = "logratio"`
7. Run the model notebook end-to-end.
8. Repeat with `TARGET = "momentum"` if you want the second target comparison.

## Important Caveats

### Patch-level, not pixel-level

The model predicts on patches, not individual pixels.

That means:

- coarse-looking target maps are expected
- tercile overlays should be interpreted as patch labels
- the research question is about settlement-scale change patterns, not exact pixel-level forecasting

### `SMOD` is a feature, not the default mask

We discussed using `SMOD` as a hard sampling filter and decided against it for the default pipeline.

Reason:

- it would reduce sample size further
- it adds another threshold to justify
- it is more valuable as contextual information for the CNN than as a mandatory inclusion rule

### If you run sensitivity tests

The main one worth comparing is:

- endpoint filter vs baseline-only 2013 filter

Do not silently swap the filter in the main pipeline without documenting it, because it changes sample size substantially in multiple countries.

## Most Important Files

- [README.md](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/README.md)
- [eda_v2.ipynb](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/eda_v2.ipynb)
- [model_v2.ipynb](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/model_v2.ipynb)
- [sam_fraley_summary.md](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/sam_fraley_summary.md)

## Short Handoff Summary

If someone asks "what are we actually running right now?", the answer is:

- `v4` data stack
- `32x32` patches with `16` stride
- endpoint-based patch retention with `BLANK_THRESH = 0.3`
- `SMOD` included as an input feature
- `logratio` as the primary target
- `momentum` as the secondary target
- LOOCV modeling in `model_v2.ipynb`

