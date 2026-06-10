# Literature Review
## Kosovo Nightlights → Built-Up Surface Prediction & Depopulation

---

## 1. Nighttime Lights as an Economic Proxy

The use of satellite nighttime lights (NTL) as a proxy for economic activity is well-established. **Henderson, Storeygard & Weil (2012)** — published in the *American Economic Review* — is the foundational paper. They developed a statistical framework showing that nighttime lights can augment (or substitute for) official GDP figures, particularly in data-poor countries. Their key insight: lights data can measure growth at sub- and supranational scales, not just countries. This directly motivates using NTL at the municipality level in Kosovo.

> Henderson, J.V., Storeygard, A. & Weil, D.N. (2012). Measuring Economic Growth from Outer Space. *American Economic Review*, 102(2), 994–1028. https://www.aeaweb.org/articles?id=10.1257/aer.102.2.994

A broader review confirms the strong relationship between nightlight luminosity and GDP at national and subnational scales, with DMSP (1992–2013) and VIIRS (2012–present) as the two main data sources:

> Nighttime Lights as a Proxy for Economic Performance of Regions. *ResearchGate*. https://www.researchgate.net/publication/360145606

One important caveat for your project: **nightlights are a better proxy in urban/peri-urban areas than in rural ones**, as documented for middle- and low-income countries:

> Are night-time lights a good proxy of economic activity in rural areas? *ScienceDirect*. https://www.sciencedirect.com/science/article/pii/S235293852100183X

---

## 2. Deep Learning for Satellite Imagery and Socioeconomic Prediction

### 2.1 The Transfer Learning Approach (your methodological ancestor)

**Jean et al. (2016)** — published in *Science* — is the most cited paper connecting nightlights, daytime imagery, and CNNs for poverty prediction. They used nightlights as a weak supervision signal to train a CNN on daytime imagery, then used the learned features to predict household consumption across five African countries (R² up to 0.75). This is the closest methodological ancestor to your project — your innovation is using NTL as the *input*, not the training signal.

> Jean, N., Burke, M. et al. (2016). Combining satellite imagery and machine learning to predict poverty. *Science*, 353(6301), 790–794. https://www.science.org/doi/10.1126/science.aaf7894

### 2.2 CNN on Multispectral Imagery for Economic Well-Being

**Yeh et al. (2020)** — *Nature Communications* — trained CNNs directly on multispectral Landsat imagery (combined with NTL) to predict village-level asset wealth across ~20,000 African villages. Their model explains 70% of variation in village wealth in held-out countries. Critically, they show that **daytime + nighttime imagery together outperform either alone** — relevant if you want to discuss future extensions.

> Yeh, C., Perez, A., Driscoll, A. et al. (2020). Using publicly available satellite imagery and deep learning to understand economic well-being in Africa. *Nature Communications*, 11, 2583. https://www.nature.com/articles/s41467-020-16185-w

### 2.3 CNN for NTL Super-Resolution and Built-Up Prediction

CNNs have been applied to convert panchromatic VIIRS-DNB NTL to higher-resolution outputs, using built-up area data as a regression target — which is almost exactly your task:

> CNN-Based Spectral Super-Resolution of Panchromatic Night-Time Light Imagery. *Sensors*, 21(22), 7662 (2021). https://www.mdpi.com/1424-8220/21/22/7662

Integrating NTL intensity and building volume to improve built-up area extraction:

> Integrating NTL Intensity and Building Volume to Improve Built-Up Areas' Extraction from SDGSAT-1 GLI Data. *Remote Sensing*, 16(13), 2278 (2024). https://www.mdpi.com/2072-4292/16/13/2278

### 2.4 Urban Land Extraction from VIIRS

VIIRS achieves over 90% accuracy in identifying construction land and urbanised areas, and outperforms DMSP in correlation with MODIS-based built-up surface — supporting your choice of VIIRS as the input data source:

> Urban Land Extraction Using VIIRS Nighttime Light Data: An Evaluation of Three Popular Methods. *ResearchGate*. https://www.researchgate.net/publication/313859524

---

## 3. Built-Up Surface Data: GHSL

The target variable in your project — built-up surface fraction — comes from the **Global Human Settlement Layer (GHSL)**, produced by the European Commission Joint Research Centre.

- Dataset: **GHS-BUILT-S R2023A** — derived from Sentinel-2 and Landsat composites, covering 1975–2030 at 10m and 100m resolutions
- Available freely via Google Earth Engine or direct download from the EU

> Pesaresi, M., Schiavina, M. et al. (2024). Advances on the Global Human Settlement Layer by joint assessment of Earth Observation and population survey data. *International Journal of Digital Earth*, 17(1). https://www.tandfonline.com/doi/full/10.1080/17538947.2024.2390454

> GHSL Dataset overview and downloads: https://ghsl.jrc.ec.europa.eu/data.php

> GHSL on Google Earth Engine: https://developers.google.com/earth-engine/datasets/catalog/JRC_GHSL_P2023A_GHS_BUILT_S

**Practical note**: GHSL provides both built-up *surface* (m²) and built-up *volume* (m³) per pixel. Built-up surface is the more direct proxy for structural presence; built-up volume would implicitly weight for building height and may be noisier for your purpose.

---

## 4. Nighttime Lights and Population Dynamics

This is the literature thread that validates your residual interpretation.

### 4.1 Decoupling of Lights and Population

A key finding directly relevant to your project: **population decline is not always coupled with decline in lighted area**. Nightlights reflect infrastructure and economic investment that persists after people leave — which is precisely the mechanism your residuals exploit.

> Nighttime lights and population changes in Europe 1992–2012. *Ambio*, 2015. https://link.springer.com/article/10.1007/s13280-015-0646-8

### 4.2 Nightlights and Migration

Regression models using nightlights explain 50–90% of variance in small-area migrations. Areas with low lights but high built-up surface are associated with out-migration — the core interpretive logic of your project.

> Nighttime Lights and Population Migration: Revisiting Classic Demographic Perspectives with an Analysis of Recent European Data. *Remote Sensing*, 12(1), 169 (2020). https://www.mdpi.com/2072-4292/12/1/169

### 4.3 Spatial Anomaly Detection

Daily and annual NTL data have been used to identify anomalies reflecting infrastructure destruction or population displacement — showing that the *residuals from expected light levels* are analytically meaningful, not just noise:

> Nighttime lights — innovative approach for identification of temporal and spatial changes in population distribution. *ResearchGate*. https://www.researchgate.net/publication/360096253

---

## 5. Kosovo Context

### 5.1 Demographic Collapse

Kosovo recorded the **world's sharpest population decline** according to 2024 World Bank data, with a -9.7% drop. The 2024 census found a resident population of 1,602,515, down from 1,739,825 in 2011 — a 9–10% loss in 13 years.

Key facts:
- ~550,000 Kosovars live in the diaspora
- Emigration concentrated in the 20–35 age bracket
- Average age rose from 29.97 (2011) to 34.84 (2024)
- Pristina continues to grow; border municipalities are severely depopulated

> Kosovo is shrinking, emptying and aging according to the 2024 population census. *Periskopi*. https://www.periskopi.com/en/kosova-po-tkurret-po-zbrazet-dhe-po-plaket-sipas-regjistrimit-te-popullsise-2024/

> Kosovo tops global population decline, Albania among top 10. *Albanian Times*. https://albaniantimes.al/kosovo-tops-global-population-decline-albania-among-top-10/

> Kosovo on the brink of a demographic change. *KosovaPress*. https://kosovapress.com/eng/admin/kosovo-on-the-brink-of-a-demographic-change-population-decline-requires-urgent-action/

### 5.2 Regional Context

Kosovo's crisis is part of a broader Western Balkans demographic pattern — Bosnia, Albania, and Serbia face similar pressures, making Kosovo an extreme but representative case for this methodology:

> The vanishing Balkans: The region's demographic crisis. *OSW Centre for Eastern Studies*, 2025. https://www.osw.waw.pl/en/publikacje/osw-commentary/2025-03-05/vanishing-balkans-regions-demographic-crisis

---

## 6. Summary Table for Background Section

| Paper | Relevance to Project |
|-------|---------------------|
| Henderson et al. (2012), *AER* | Foundational justification for NTL as economic proxy |
| Jean et al. (2016), *Science* | CNN + NTL for socioeconomic prediction — methodological ancestor |
| Yeh et al. (2020), *Nature Comms* | CNN on satellite imagery for economic well-being — closest method |
| Pesaresi et al. (2024), *Int. J. Digital Earth* | GHSL built-up surface — your target variable |
| NTL & population changes in Europe (2015), *Ambio* | Decoupling of lights and population — validates residual logic |
| NTL & migration (2020), *Remote Sensing* | NTL predicts migration — validates interpretive framework |
| Kosovo 2024 census | Ground truth for residual validation |

---

## 7. Key Gaps Your Project Fills

1. **Geography**: None of the CNN-based poverty/development papers focus on the Western Balkans or post-conflict small states.
2. **Mechanism**: Prior work uses NTL to *predict* development; your project uses *prediction errors* to detect depopulation — a methodological inversion that is novel.
3. **Validation**: You validate against an actual census rather than survey data, giving harder ground truth.
