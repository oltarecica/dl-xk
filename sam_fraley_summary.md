# Sam Fraley Summary

## Scope Of This Session

This session focused on three connected areas:

1. Updating the EDA and modeling notebooks from the old `v3` raster stack to the new `v4` stack.
2. Clarifying the patch-level target definitions and patch filtering logic.
3. Testing whether a stricter baseline-only nightlight filter would be a better sampling rule than the current endpoint-based filter.

The work was done primarily in [eda_v2.ipynb](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/eda_v2.ipynb) and [model_v2.ipynb](/abs/path/C:/Users/sffra/Projects/BSE%202025-2026/kosovo-dl/dl-xk/model_v2.ipynb), with supporting discussion around the Earth Engine export pipeline that produces `balkans_{country}_v4.tif`.

## Main Dataset Understanding

We clarified the raster stack structure and data provenance.

### `v3` stack

The original Balkans stack in `v3` had 10 bands:

0. `viirs_2013`
1. `viirs_2014`
2. `viirs_2015`
3. `viirs_2016`
4. `builtup_fraction`
5. `population`
6. `elevation`
7. `slope`
8. `infra_proximity`
9. `viirs_2017`

Important clarification: in the Balkans export script, `builtup_fraction` in `v3` came from ESA WorldCover aggregated to 500m, not GHSL built surface.

### `v4` stack

We decided to move to `v4`, which adds `SMOD` and aligns the built-up, population, settlement, and proximity context more cleanly around GHSL.

The `v4` stack has 11 bands:

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

`SMOD` is intended as a feature channel, not as the default sampling mask.

## Earth Engine Export Decisions

We rewrote the Earth Engine export cell for `v4` and resolved two export errors:

1. `Image.resample: Invalid interpolation mode: nearest`
   - Cause: `ee.Image.resample()` does not accept `"nearest"`.
   - Fix: remove `.resample("nearest")` entirely from `smod_code`.
   - Rationale: nearest-neighbor behavior is effectively what we want for a categorical class raster anyway.

2. `Exported bands must have compatible data types; found inconsistent types: Float32 and Float64`
   - Cause: mixed band dtypes inside the export stack.
   - Fix: apply `.toFloat()` to the final stacked image before export.

We also shifted `builtup_fraction` in the proposed `v4` export to GHSL built surface so the contextual layers are more internally consistent.

## Target Variable Changes

Inside `extract_patches()` in `eda_v2.ipynb`, the old percent-change target was replaced.

### Old target

`pct_change = (v17[0] - vi[0]) / (vi[0] + 1e-6) * 100`

### New target 1: log-ratio

`log_ratio = np.log1p(v17[0]) - np.log1p(vi[0])`

This is safe because VIIRS values are already clipped to be nonnegative in `load_country()`.

### New target 2: departure from momentum

We added a second patch-level target:

1. Take the per-patch mean VIIRS value for 2013, 2014, 2015, and 2016.
2. Transform those means with `log1p`.
3. Fit a linear trend over years `0, 1, 2, 3`.
4. Extrapolate to year `4` as the expected 2017 log intensity.
5. Compute:

`departure_from_momentum = actual_2017_log - predicted_2017_log`

This gives a patch-level measure of whether 2017 is above or below the patch's recent trajectory.

### Label construction

For both targets, the logic stayed the same:

1. Compute patch-level scalar values.
2. Take the 33rd and 67th percentiles.
3. Use `np.digitize()` to assign low, mid, and high tercile labels.

The notebook now saves:

- `{country}_patches.npy`
- `{country}_labels_logratio.npy`
- `{country}_labels_momentum.npy`

## EDA Notebook Changes

Several changes were made in `eda_v2.ipynb`.

### `extract_patches()` updates

The function now:

- computes both `log_ratio` and `departure_from_momentum`
- returns three outputs:
  - `patches`
  - `labels_logratio`
  - `labels_momentum`
- includes `SMOD` in the patch tensor when using `v4`

### `load_country()` updates

`load_country()` now reads `balkans_{country}_v4.tif` and returns:

- `viirs_input`
- `viirs_2017`
- `builtup`
- `pop`
- `elev`
- `slope`
- `prox`
- `smod`

### Visual diagnostics added or updated

We added or revised cells for:

- target maps for log-ratio and momentum
- two-row class balance plots
- patch-tercile overlays on grayscale VIIRS backgrounds
- patch-size comparison maps for `8x8`, `32x32`, and `64x64`
- Kosovo vs Serbia patch coverage comparisons
- filter sensitivity diagnostics

We also clarified that these visualizations are patch-level, not pixel-level. The apparent coarseness is expected because the model predicts on patches, not individual pixels.

## Model Notebook Changes

`model_v2.ipynb` was updated to align with the new targets and the new patch tensor layout.

### Target switch

We added:

`TARGET = "logratio"`

with the option to switch to `"momentum"`.

### Label loading

Labels are now loaded from:

`{country}_labels_{TARGET}.npy`

### Results path

The results pickle path now includes the target name:

`data/loocv_results_v2_{TARGET}.pkl`

### `v4` channel usage

The model now assumes the patch tensor includes `SMOD` and excludes only `viirs_2017` from inputs.

Current input channels:

`INPUT_CHANNELS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]`

That means the model uses:

- VIIRS 2013-2016
- built-up fraction
- population
- elevation
- slope
- infrastructure proximity
- SMOD code

and excludes:

- `viirs_2017` at channel 10

## Patch Size Understanding

We clarified an important modeling point:

- The current model predicts on patches, not pixels.
- The coarse tercile maps are therefore honest representations of the actual training instances.
- `8x8` is very dense but likely too local and noisy.
- `64x64` is much coarser and yields relatively few patches for small countries.
- `32x32` appears to be a reasonable compromise and is especially important for keeping enough instances in smaller-country folds.

We also discussed why Serbia looks much denser than Kosovo under `32x32`: Serbia has a larger spatial extent and far more grid positions that pass the retention rule.

## Filtering Discussion

We spent substantial time on the patch retention rule.

### Current main filter

The current pipeline retains a patch if:

1. the `viirs_2017` patch is not too NaN-heavy
2. the patch mean of `max(viirs_2013, viirs_2017)` exceeds `BLANK_THRESH`

This is an endpoint-based filter.

### Baseline-only alternative

The stricter alternative retains a patch if:

1. the `viirs_2017` patch is not too NaN-heavy
2. the patch mean of `viirs_2013` alone exceeds `BLANK_THRESH`

This is cleaner conceptually, but it is more restrictive.

### Key conceptual conclusion

The endpoint filter is not classic input leakage because `viirs_2017` is not a model feature. However, it is still outcome-conditioned sample selection because 2017 affects whether a patch is included at all.

Even so, we concluded that it is defensible for the main analysis because it avoids throwing away many settlement-adjacent patches that appear genuinely meaningful.

## Filter Sensitivity Results

We ran a direct sensitivity check comparing the current endpoint filter to the baseline-only 2013 filter.

Results:

| country | endpoint_filter | baseline2013_filter | delta | pct_change |
| --- | ---: | ---: | ---: | ---: |
| Albania | 459 | 262 | -197 | -42.9 |
| Bosnia_and_Herzegovina | 959 | 562 | -397 | -41.4 |
| Kosovo | 230 | 200 | -30 | -13.0 |
| Montenegro | 220 | 126 | -94 | -42.7 |
| North_Macedonia | 444 | 273 | -171 | -38.5 |
| Serbia | 1652 | 1310 | -342 | -20.7 |

### Interpretation

This was the most important empirical finding of the session.

- Kosovo is fairly stable under the stricter baseline-only filter.
- Serbia changes moderately.
- Albania, Bosnia and Herzegovina, Montenegro, and North Macedonia each lose roughly 39-43% of their retained patches.

This means the baseline-only filter is not a small cleanup. It would materially change the sample composition across countries and reduce sample size sharply in several of the smaller or more spatially fragmented cases.

### Decision

We decided to keep the endpoint-based filter as the main sampling rule.

The baseline-only version should be treated as a sensitivity analysis, not the default pipeline.

## SMOD: Feature Or Filter?

We discussed whether `SMOD` should be used to restrict sampling.

### Why not use `SMOD` as the default filter

- It could reduce sample size further.
- It would introduce another thresholding decision to justify.
- It risks excluding valid nightlit patches in lower-density settlement classes.

### Why use `SMOD` as a feature

- It gives the model settlement context directly.
- It preserves flexibility.
- It is easier to justify scientifically as explanatory context rather than a hard inclusion rule.

### Session conclusion

Use `SMOD` as an input channel in `v4`, not as the default patch filter.

## What We Learned Substantively

The main substantive lessons from this session are:

1. The patch-level framework is working as intended and should be thought of as predicting settlement-scale outcomes, not pixel-scale outcomes.
2. `32x32` remains a sensible working scale because it balances spatial context with sample size.
3. The stricter baseline-only nightlight filter removes too many patches in several countries to be a good default choice.
4. `SMOD` is more valuable as a contextual feature than as a mandatory sampling mask.
5. The endpoint filter produces geographically plausible retained coverage while maintaining better sample support across countries.

## Recommended Next Steps

1. Regenerate patch `.npy` files from the updated `eda_v2.ipynb` using the `v4` stack.
2. Run `model_v2.ipynb` on the `v4` patch tensors with `TARGET = "logratio"` first.
3. Run the same model with `TARGET = "momentum"` as a direct comparison.
4. If time permits, do one formal robustness rerun with the baseline-only filter and compare results to the endpoint-filter main run.
5. In the poster or writeup, describe the endpoint-vs-baseline filter comparison explicitly as a sensitivity check.

## Suggested Methods Wording

One concise summary of the filtering decision:

> A sensitivity check replacing the endpoint-based patch retention rule with a baseline-only 2013 nightlight filter reduced retained patches by 13% in Kosovo, 21% in Serbia, and roughly 39-43% in Albania, Bosnia and Herzegovina, Montenegro, and North Macedonia. Because this substantially reduced sample size in several countries without clearly improving geographic plausibility, the endpoint-based filter was retained for the main analysis.

