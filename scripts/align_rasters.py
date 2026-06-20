"""
Reproject GHSL built-up surface and GHS-POP (both in ESRI:54009 Mollweide)
onto the VIIRS pixel grid (EPSG:4326).

Outputs (same CRS, shape, and pixel boundaries as viirs_nightlights_kosovo_2023.tif):
  ghsl_builtup_kosovo_2020_aligned.tif
  ghsl_population_kosovo_2020_aligned.tif
"""

import numpy as np
import rasterio
from rasterio.warp import reproject, Resampling

viirs_path = "data/viirs_nightlights_kosovo_2023.tif"

with rasterio.open(viirs_path) as viirs_src:
    ref_crs       = viirs_src.crs
    ref_transform = viirs_src.transform
    ref_shape     = (viirs_src.height, viirs_src.width)
    ref_profile   = viirs_src.profile.copy()

ref_profile.update(dtype=rasterio.float32, count=1, nodata=None)


def align(src_path, out_path, resampling):
    with rasterio.open(src_path) as src:
        data = src.read(1).astype(np.float32)
        # Replace NaNs with 0 before reprojecting so they don't bleed into neighbours
        data = np.nan_to_num(data, nan=0.0)
        src_crs       = src.crs
        src_transform = src.transform

    aligned = np.zeros(ref_shape, dtype=np.float32)

    reproject(
        source        = data,
        destination   = aligned,
        src_transform = src_transform,
        src_crs       = src_crs,
        dst_transform = ref_transform,
        dst_crs       = ref_crs,
        resampling    = resampling,
    )

    with rasterio.open(out_path, 'w', **ref_profile) as dst:
        dst.write(aligned, 1)

    with rasterio.open(out_path) as result:
        d = result.read(1)
        print(f"{out_path.split('/')[-1]}")
        print(f"  Shape     : {result.shape}  CRS: {result.crs}")
        print(f"  Min/Max   : {d.min():.4f} / {d.max():.4f}")
        print(f"  Zero pixels: {(d==0).sum()} ({100*(d==0).mean():.1f}%)")
        print(f"  Aligned   : {result.shape == ref_shape and result.transform == ref_transform}")


print("=== Aligning GHSL built-up surface ===")
align(
    src_path   = "data/ghsl_builtup_kosovo_2020.tif",
    out_path   = "data/ghsl_builtup_kosovo_2020_aligned.tif",
    resampling = Resampling.average,   # mean built-up fraction across 100m → 500m
)

print("\n=== Aligning GHS-POP population ===")
align(
    src_path   = "data/ghsl_population_kosovo_2020.tif",
    out_path   = "data/ghsl_population_kosovo_2020_aligned.tif",
    resampling = Resampling.sum,       # sum population counts when aggregating
)
