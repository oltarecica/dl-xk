import rasterio
import numpy as np
import matplotlib.pyplot as plt

viirs_path = "data/viirs_nightlights_kosovo_2025.tif"
ghsl_path  = "data/ghsl_builtup_kosovo_2020_aligned.tif"

# --- 1. Basic properties ---
print("=== Raster properties ===")
for path in [viirs_path, ghsl_path]:
    with rasterio.open(path) as src:
        data = src.read(1)
        print(f"\n{path.split('/')[-1]}")
        print(f"  Shape      : {data.shape}")
        print(f"  CRS        : {src.crs}")
        print(f"  Transform  : {src.transform}")
        print(f"  Min / Max  : {np.nanmin(data):.4f} / {np.nanmax(data):.4f}")
        print(f"  NaN pixels : {np.isnan(data).sum()}")
        print(f"  Zero pixels: {(data == 0).sum()} ({100*(data==0).mean():.1f}%)")

# --- 2. Alignment check ---
print("\n=== Alignment check ===")
with rasterio.open(viirs_path) as v, rasterio.open(ghsl_path) as g:
    same_shape     = v.shape == g.shape
    same_transform = v.transform == g.transform
    same_crs       = v.crs == g.crs
    print(f"  Same shape     : {same_shape}  {v.shape}")
    print(f"  Same transform : {same_transform}")
    print(f"  Same CRS       : {same_crs}  {v.crs}")
    viirs = v.read(1).astype(np.float32)
    ghsl  = g.read(1).astype(np.float32)

# --- 3. Correlation (sanity: brighter = more built-up?) ---
mask = (viirs > 0) & (ghsl > 0)
corr = np.corrcoef(viirs[mask], ghsl[mask])[0, 1]
print(f"\n=== Pixel-level correlation (non-zero pixels) ===")
print(f"  Pearson r = {corr:.4f}  (expect positive, ~0.4-0.7)")

# --- 4. Visual check ---
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].imshow(viirs, cmap='inferno', vmin=0, vmax=10)
axes[0].set_title("VIIRS Nightlights 2025\n(avg radiance nW/cm2/sr)")
axes[0].axis('off')

axes[1].imshow(ghsl, cmap='YlOrRd', vmin=0, vmax=0.5)
axes[1].set_title("GHSL Built-Up Fraction 2020\n(aligned to VIIRS grid)")
axes[1].axis('off')

axes[2].scatter(viirs[mask], ghsl[mask], s=0.5, alpha=0.3, c='steelblue')
axes[2].set_xlabel("VIIRS radiance")
axes[2].set_ylabel("GHSL built-up fraction")
axes[2].set_title(f"Scatter (r = {corr:.3f})\nn = {mask.sum():,} pixels")

plt.tight_layout()
plt.savefig("data/sanity_check.png", dpi=150)
plt.show()
print("\nPlot saved to data/sanity_check.png")
