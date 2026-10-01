# Rev B current hardware digital recertification

Date: 2026-09-30. This is evidence for the current mechanical/electrical working tree, not a fabrication, energization, certification or complete system release. Firmware and campus integration have their own evidence.

## Result

The 23 mechanical and 6 electrical stale freeze entries were investigated against the actual pre-migration Git objects, rather than accepted by replacing hashes. Of the 29 files, 24 differed only in project/model identifiers, two additionally removed trailing Markdown whitespace, and three were PDFs. All original SHA-256 values were recovered from Git. The PDFs were regenerated from current sources and their complete 11 pages rendered and visually inspected.

The machine-readable trace is `hardware_recertification.json`. It records original blob IDs, former/current hashes, disposition, current evidence hashes and explicit physical HOLD gates. `hardware_validation_run.txt` preserves the actual current command outputs. No physical CAD or routed PCB design change was necessary.

## Actual checks rerun

- Native KiCad 9.0.2 DRC: 0 violations, 0 unconnected pads, 0 footprint errors; ERC: 0 errors and 0 warnings
- Schematic/main-board pin audit: all 321 numbered main-board keys match; the complete assembly graph covers 348 numbered terminals
- Native supported-rule negative control rejects the synthetic 6 mm domain gap; independent checker rejects a deliberately shifted hot pad
- Fresh separate six-sheet schematic, placement and copper-recipe rebuild passes ERC/DRC and both negative controls. Its physical signature matches the retained PCB: four layers, footprints/pads/nets, all copper items and zone outlines. Generated UUIDs and library nickname/container metadata are not physical comparisons
- Fresh mechanical source build and exports equal retained native geometry at a 1e-10 BRep numeric tolerance: 72 base objects, 72 delivery objects, 235 combined native objects including the nonphysical reservation, and 144 main-board placement/body/lead objects
- Integrated fit, prescribed contact insertion, 11 shutter states, modeled conductive joint connectivity and continuous PE checks reran successfully
- Full insulation-domain audit ran from all current inputs, without incremental reuse: no inputs changed during the run; minimum nominal exposed-primary/main-board separation is 8.516644688 mm against the project-only 8.4 mm screen
- Retained lightweight STEP roundtrip contains 234 valid physical solids. Detailed STEP roundtrip contains 3223 valid solids with relative summed-volume difference 2.12e-8
- Face/polarity drawing, six-sheet schematic and four copper-review pages were regenerated. The source-based drawing snapshot and current preview were refreshed

Fresh reconstruction details and source hashes are in `hardware_geometry_rebuild.json`. Electrical handoff now binds all six schematic sheets, rules, negative controls, source graph and checker scripts, not just the top-level sheet. Mechanical freezing uses the actual rerun reports and source hashes. Validation history remains in Git instead of creating new duplicate working-tree archives.

## Reproduce without physical changes

1. With KiCad 9, FreeCAD 1.0, system pcbnew, Inkscape, ReportLab and pypdf available, copy the checkout into a separate temporary worktree/directory. Keep the Rev B controller/meter/feedback/thermal source modules and `electronics/scripts/sexpr_util.py`; integrated generation still depends on them
2. In that separate copy, run `mechanical/rev_b/build_base.py`, `export_release.py`, `verify_exports.py` with `/usr/bin/python3`; run `electronics/rev_b/integrated/scripts/export_geometry.py --bodies-only`; run `bash electronics/rev_b/integrated/scripts/rebuild.sh --no-geometry`
3. Against the retained checkout, rerun the mechanical integrated-fit, contact, shutter, connectivity, full insulation and export verifiers, including `export_detailed_assembly.py --verify-existing`. Rerun native/independent electrical controls, rear termination and `finalize_validation.py`. Use a writable temporary KiCad/XDG configuration directory
4. Run `/usr/bin/python3 scripts/verify_hardware_rebuild.py --rebuilt-root /path/to/the/separate/copy`. Regenerate and visually review the PDFs if their sources changed
5. Only after those checks pass, refresh `mechanical/rev_b/finalize_snapshot.py`, electrical source hashes, and `scripts/finalize_hardware_handoff.py`. Update the recertification record to the actual run; do not reuse a stale review claim
6. Read-only guards: `python3 -m unittest discover -s tests/hardware -v` and `python3 scripts/validate_hardware_evidence.py`. The latter is also called by `scripts/validate_release_rev_b.py`

## Physical HOLD remains

The 8.5166 mm nominal 3D result is not qualified free-air clearance or creepage. The component-land audit still has an 8.10 mm nominal minimum, and the remote thermal pickup depends on 0.5 mm of unqualified solid insulation. None of these numbers is a standards-compliance result.

No manufacturing, flashing, energization or physical test occurred. Manufactured insulation/PE/dielectric/leakage, 16 A enclosed temperature rise, real load inrush, fault containment, total-clearing fuse coordination, contact force/endurance, materials and mechanical gauges, traceable metrology, thermal response, RF and EMC remain open. See `../docs/ENGINEERING_RELEASE_GATES.md`.
