# CARBENTRA visual engineering

This directory is the visual layer of **碳迹未来 · CARBENTRA**. The canonical current assets are under [`rev_b/`](rev_b/); Rev A is retained only as an engineering-history baseline.

All product geometry is derived from the shared mechanical and ECAD sources in their common millimetre coordinate frame. Blender converts those engineering exports to presentation units; it does not substitute an unrelated shell or AI-generated product geometry.

## Current baseline

- **Platform:** CARBENTRA
- **Device:** CARBENTRA Plug
- **Revision:** CARBENTRA-P16-EVT-B
- **Canonical scene:** `rev_b/carbentra_studio.blend`
- **Detailed GLB:** `rev_b/exports/carbentra_assembly.glb`
- **Twin GLB:** `rev_b/exports/carbentra_twin_light.glb`
- **Animation:** `rev_b/animation/carbentra_exploded.mp4`
- **Renders:** `rev_b/renders/`

The active scene includes the CARBENTRA product mark and the Chinese project identity **碳迹未来**. Display-only transparent, exploded and section views are inspection devices, not material or manufacturing claims.

## Reproduce Rev B

From the repository root, after the mechanical and ECAD exports exist, set the Rev B source paths described in [`rev_b/README.md`](rev_b/README.md) and run:

```sh
blender -b --python visuals/scripts/build_studio.py -- all
python visuals/scripts/compose_sheets_zh.py
python visuals/scripts/validate_deliverables.py
```

The Blender pipeline supports `CARBENTRA_USE_GPU=1` for a local CUDA/OptiX render path when available. The annotated-sheet scripts use the repository font asset instead of an OS-specific font path.

## Revision policy

[`revA_baseline/`](revA_baseline/) is kept to document engineering evolution. It must not be mixed with Rev B dimensions, PCB placement, validation results or release status. Generated archive media that still carried obsolete branding is intentionally excluded from the current canonical set; Git history remains the provenance record.

## Engineering boundary

Photoreal lighting does not imply a fabricated or tested product. The 220 V AC / 16 A target remains a design target until physical safety, gauge, temperature-rise, insulation, protection, EMC, calibration and reliability work is complete.
