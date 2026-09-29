---
license: cc-by-sa-4.0
task_categories:
- image-segmentation
- object-detection
tags:
- satellite-imagery
- remote-sensing
- building-footprints
- spacenet
- geospatial
size_categories:
- n<1K
---

# SpaceNet Buildings (Vegas) — 20-Chip Smoke-Test Sample

**This is a tiny 20-chip sample, not a full dataset.** It exists to reproducibly
smoke-test a U-Net vs YOLO building-detection training pipeline end-to-end — not to
train a real model. See the companion model repo
[`khalilurrahmanridoykhan/unet-vs-yolo-buildings-smoketest`](https://huggingface.co/khalilurrahmanridoykhan/unet-vs-yolo-buildings-smoketest)
and the source code at
[github.com/khalilurrrahmanridoykhan/best-model-for-satellite-imagery](https://github.com/khalilurrrahmanridoykhan/best-model-for-satellite-imagery).

## Source and license

Derived from [SpaceNet Buildings v2](https://spacenet.ai/datasets/) (AOI_2_Vegas),
released under **CC BY-SA 4.0** by the SpaceNet partners (Maxar/DigitalGlobe imagery,
CosmiQ Works, and other SpaceNet contributors — see spacenet.ai for full attribution).
This sample (20 chips, pulled from the public `spacenet-dataset` S3 bucket) and any
derivatives are shared under the same **CC BY-SA 4.0** license, per its share-alike
terms.

The full dataset (thousands of chips) is not included here — pull it directly with
[`scripts/download_data.py`](https://github.com/khalilurrrahmanridoykhan/best-model-for-satellite-imagery/blob/main/scripts/download_data.py)
in the source repo (anonymous S3 access, no AWS account needed).

## Contents

- `raw/images/*.tif` — 20 raw satellite chips (RGB, georeferenced)
- `raw/labels/*.geojson` — building-footprint polygons for each chip
- `split.json` — the train/val/test split (14/3/3) used for the smoke test, by whole
  chip (no chip appears in more than one split)

Rasterized U-Net masks and YOLO-format boxes are *derived* from `raw/` by
[`notebooks/02_build_labels.ipynb`](https://github.com/khalilurrrahmanridoykhan/best-model-for-satellite-imagery/blob/main/notebooks/02_build_labels.ipynb)
in the source repo rather than duplicated here.

## Known data quirks (documented, not hidden)

A few of the underlying SpaceNet labels are degenerate `Point` or `MultiPolygon`
geometries rather than clean `Polygon`s — handled in the source pipeline's
`filter_polygon_geometries()`, not filtered out of this raw sample.
