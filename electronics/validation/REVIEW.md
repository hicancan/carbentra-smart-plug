# Final validation interpretation

- **ERC:** 0 errors, 0 warnings on the final grouped A3 source
- **Pin/net consistency:** 104 assigned pins across 33 components agree between the real KiCad netlist and physical PCB pads
- **PCB geometry DRC:** 0 violations; no shorts, clearance violations, courtyard overlaps, drill or silk errors
- **Low-voltage routing:** no unconnected items
- **Hazardous routing:** 9 intentional unconnected items on L_AUX_FUSED, L_FUSED, L_SWITCHED, L_NC_UNUSED and N; full list in `drc.rpt`
- **Footprint invariance:** all 37 footprints (33 components + 4 holes) retained their fixed position, rotation, identifier and pad geometry during final routing closure
- **3D:** native KiCad board/copper STEP exported successfully; package-envelope assembly exports are simplified geometry, not vendor-detailed component solids

PWR_FLAG declarations state where the circuit is driven: external auxiliary line/neutral, buck output through the inductor, and the relay's unused NC terminal that becomes live from the common contact. They do not assert voltage safety, fuse operation or hardware correctness. NC is externally unwired but is never treated as a safe floating pad.

The preliminary 8 mm hazardous-to-control clearance rule is checked in the PCB's 2D copper geometry. It does not establish full creepage, primary-to-primary insulation, 3D clearance to conductors/fasteners, material group, altitude, pollution degree, or a product-standard compliance conclusion. Those are release gates.

Native reports are unfiltered. Intermediate routing reports are retained for development provenance; only `erc.rpt`, `drc.rpt`, `net_pin_consistency.json`, `footprint_invariance.json` and `final_summary.json` describe the final canonical release. No physical bench, metrology, relay-load, thermal, EMC, dielectric or production test has run. The board must not be fabricated or energized from this development release.
