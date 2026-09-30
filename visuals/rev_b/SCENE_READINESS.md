# Rev B scene preparation

Final output directories are `renders/`, `exports/`, and `animation/` under this folder. `_preview/` is exclusively provisional and must not be delivered as verified engineering output.

- Cameras and lights scale to the 108 × 93 × 65 mm enclosure.
- Front labels follow local OFF and recessed REARM coordinates.
- Mechanical import uses explicit manifest parts and validates unmodified vertices.
- MainB OBJ has board-local coordinates: set `CARBENTRA_PCB_Z_MM=11.5` for its assembly placement.
- Remote HeadB will be imported from a pretransformed OBJ via `CARBENTRA_HEAD_OBJ`.
- `CARBENTRA_MECHANICAL_DIR` and `CARBENTRA_PCB_OBJ` select authoritative Rev B sources; `CARBENTRA_OUTPUT_DIR` selects this folder only after integrated fit freeze.
- `compose_sheets_zh.py` composes Chinese technical annotations.
- Full native geometry remains selectable; light GLB batches actual trace/pad/via geometry.

Final render/export must wait for verified mechanical fit and the complete MainB + HeadB source set. These preparation notes are not a release approval.
