// ============================================================
// GEE Export Script — Kosovo Nightlights + Built-Up Surface
// Paste this into code.earthengine.google.com and click Run,
// then go to Tasks tab (top right) and click Run on each task.
// Both files will appear in your Google Drive under "dl-xk-data".
// ============================================================

// --- Kosovo bounding box ---
var kosovo = ee.Geometry.Rectangle([20.0, 41.8, 21.8, 43.3]);

// ============================================================
// 1. VIIRS Nighttime Lights — 2025 annual median composite
//    Dataset: NOAA VIIRS DNB monthly composites (cloud-masked)
//    Band:    avg_rad (average radiance, nW/cm²/sr)
//    Median across all 12 months for a stable annual composite.
// ============================================================
var viirs = ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
  .filterDate('2025-01-01', '2025-12-31')
  .median()
  .select('avg_rad');

Export.image.toDrive({
  image: viirs,
  description: 'viirs_nightlights_kosovo_2025',
  folder: 'dl-xk-data',
  fileNamePrefix: 'viirs_nightlights_kosovo_2025',
  region: kosovo,
  scale: 500,
  maxPixels: 1e9
});

// ============================================================
// 2. GHSL Built-Up Surface — 2020 epoch (last real satellite obs)
//    Dataset: JRC/GHSL/P2023A — derived from Sentinel-2 + Landsat
//    Band:    built_surface (m² per 100m pixel) → divided by
//             10000 to give fraction [0, 1].
//    2020 is the most recent epoch with actual satellite data.
//    2025 exists in P2023A but is a model projection, not observed.
//    The 5-year gap (2020 structure vs 2025 light) is the signal:
//    buildings persist after people leave, lights go dark first.
// ============================================================
var ghsl = ee.ImageCollection('JRC/GHSL/P2023A/GHS_BUILT_S')
  .filter(ee.Filter.date('2020-01-01', '2021-01-01'))
  .first()
  .select('built_surface')
  .divide(10000)
  .rename('built_fraction');

Export.image.toDrive({
  image: ghsl,
  description: 'ghsl_builtup_kosovo_2020',
  folder: 'dl-xk-data',
  fileNamePrefix: 'ghsl_builtup_kosovo_2020',
  region: kosovo,
  scale: 500,
  maxPixels: 1e9
});

// ============================================================
// 3. GHS-POP Population Grid — 2020 epoch (last real satellite obs)
//    Dataset: JRC/GHSL/P2023A
//    Band:    population_count (people per 100m pixel)
//    Exported at 500m: population sums when aggregating.
// ============================================================
var ghspop = ee.ImageCollection('JRC/GHSL/P2023A/GHS_POP')
  .filter(ee.Filter.date('2020-01-01', '2021-01-01'))
  .first()
  .select('population_count');

Export.image.toDrive({
  image: ghspop,
  description: 'ghsl_population_kosovo_2020',
  folder: 'dl-xk-data',
  fileNamePrefix: 'ghsl_population_kosovo_2020',
  region: kosovo,
  scale: 500,
  maxPixels: 1e9
});

// ============================================================
// Quick preview
// ============================================================
Map.setCenter(20.9, 42.55, 8);

Map.addLayer(viirs.clip(kosovo), {
  min: 0, max: 5,
  palette: ['000000', '0d0221', '1a0a3c', 'ffffff']
}, 'VIIRS 2025');

Map.addLayer(ghsl.clip(kosovo), {
  min: 0, max: 0.5,
  palette: ['ffffff', 'ffcc00', 'ff6600', 'cc0000']
}, 'GHSL Built-Up 2020');

Map.addLayer(ghspop.clip(kosovo), {
  min: 0, max: 100,
  palette: ['ffffff', 'a8d5a2', '3a7d44', '1a3c1f']
}, 'GHS-POP 2020');
