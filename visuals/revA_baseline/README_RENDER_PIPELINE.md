# CarbonMirror studio assets

All model geometry comes from the shared mechanical STL assembly and electronic OBJ assembly, in their common millimetre coordinate frame. The scene converts those exact engineering exports to metres. No image-generation substitute or unrelated visual shell is used.

## Reproduce

From the repository root, after generating mechanical and electronic files:

```sh
blender -b --python visuals/scripts/build_studio.py -- preview
blender -b --python visuals/scripts/build_studio.py -- hero
blender -b --python visuals/scripts/build_studio.py -- technical
blender -b --python visuals/scripts/build_studio.py -- animation
python visuals/scripts/compose_sheets.py
```

Use `all` to run everything in one process. Blender 4.3.2; Python/Pillow for annotated sheets. Fonts: DejaVu Sans and Noto Sans CJK. Render camera/lighting, brand pad-print lettering and small render-only edge bevels are presentation additions. The engineering geometry remains in mechanical/ and electronics/.

## Deliverables

- `carbonmirror_studio.blend`: assembled source, named CAD/ECAD parts, materials, physical studio lighting and camera
- `carbonmirror_animation.blend`: animated explosion/reassembly source
- `exports/carbonmirror_assembly.glb`: named selectable-part assembly, metre units
- `renders/01_hero_ivory.png`, `02_hero_detail.png`: 2400 × 2000 Cycles studio images
- `renders/03_rear_interface.png`: rear input interface
- `renders/04_internal_architecture.png`: exterior removed to inspect shared structure
- `renders/05_transparent_inspection.png`: nonphysical diagnostic ghost-shell treatment (not a transparent material proposal)
- `renders/06_exploded_annotated.png`: labeled exploded assembly
- `renders/07_six_view_sheet.png`: labeled orthographic sheet
- `renders/08_section_annotated.png`: true display-only longitudinal section
- `renders/09_pcb_assembly.png`: source-routed PCB inspection with footprint package envelopes
- `renders/view_*.png`: individual orthographic images
- `animation/carbonmirror_exploded.mp4`: smooth 24 fps engineering presentation

## Meaning and limits

CM-S16-EVT-A is an engineering development design with verification pending. The interface is a single three-pin, 16 A-class design target, not a claim of certified dimensions, universal compatibility, successful manufacture or safe operation. Electronic body solids are footprint-derived package envelopes, not vendor-detailed solids. Transparent and exploded views are inspection visualizations. Colour and candidate material choices are presentation specifications, not material qualification.

The assembly explosion uses mechanical manifest offsets and moves the entire electronics group together. It illustrates architecture; it is not a validated manufacturing assembly procedure. Photoreal lighting does not imply a fabricated or tested product.

### Animation representation

The MP4 is studio-shaded CAD animation (Workbench), not a photoreal film. The animation-specific Blender source batches components by rigid explosion layer for rendering performance; each layer records its original `source_members`. The assembled studio source and GLB retain individual selectable parts. All layer geometry is converted from the same imported assembly, without a substitute shell. Frames use smooth Bezier easing with assembled/exploded pauses and a slow camera arc.

The half-section sheet applies a display-only Boolean cut at X = 0 to copies of the original geometry. It does not modify native CAD or imply that parts have been fabricated and sectioned.

Routed copper and vias, when present, are imported from the electronics source export. The green trace material is a routing-inspection overlay, not a finished soldermask specification. Mask openings, tenting and manufacturing finish remain unqualified. The animation title/footer is added during FFmpeg encoding.
