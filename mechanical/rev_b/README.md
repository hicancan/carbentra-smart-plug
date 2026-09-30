# CARBENTRA · CM-S16-EVT-B

Original integrated smart-plug engineering development assembly. Nominal enclosure 108 × 93 × 65 mm; one 100 × 85 mm main PCB plus a remote temperature pickup. This is a reviewable digital design, not an authorization to fabricate or energize mains hardware.

## Main files
- `CM-S16-EVT-B.FCStd`: parameterized mechanical source with editable enclosure, shutter and contact-gap inputs
- `CM-S16-EVT-B_mechanical.step`: 71 mechanical parts
- `CM-S16-EVT-B_system_assembly.FCStd` / `.step`: mechanical parts, 144 actual exported PCB placement/body/lead objects and 19 transformed head solids
- `parts_manifest.json`, `meshes/`, `parts/`: common-frame meshes, individual STEP parts, materials/grouping and exploded offsets
- `assembly_world_bounds.json`: tessellated per-object and aggregate bounds for transform verification
- `contacts_inserted_nominal.step`, `contacts_inserted_maximum_reference.step`: prescribed 1.8 / 1.95 mm blade-opening states, separate from the unloaded 1.7 mm contact state
- `docs/`: dimensioned front/rear polarity drawing, engineering description and tolerance/release gates

## Validation evidence
`integrated_fit_report.json` records BRep validity, intentional interfaces and unintended interference separately. `contact_engagement_report.json` distinguishes intended spring engagement from rigid insertion obstruction. `shutter_kinematic_report.json` tests the closed, single-pawl and released travel states. `polarity_connectivity_report.json` checks modeled external conductive joints and continuous PE. `insulation_domain_report.json` / `.md`, when generated, are a separate primary/isolated proximity review: collision-free geometry is not electrical-safety approval.

The PCB package solids include nominal/max body envelopes and explicit lead volumes, not complete vendor internal CAD. Detailed PCB copper is supplied separately by the electronics project. Female receptacle gauges, contact force/endurance, dielectric qualification, solder/weld/crimp processes, real thermal behavior, enclosure retention, and wall-socket loading remain release gates.

## Reproduce
Use the installed FreeCAD Python environment with `/usr/lib/freecad-python3/lib` on `sys.path`. Run, in order: `build_base.py`, `validate_integrated_fit.py`, `validate_contact_engagement.py`, `validate_shutter.py`, `audit_connectivity.py`, and `export_release.py`. The build-stage file is intentionally named `CM_S16_B_base_provisional.FCStd`; the export script produces the named deliverables above. Keep `socket_b_features.py`, `power_links.py` and `design_parameters.json` alongside native files for proxy regeneration. Rev A files are independent and unchanged.
