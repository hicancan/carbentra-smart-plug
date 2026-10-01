# CARBENTRA · CARBENTRA-P16-EVT-B electronics

**Routed engineering development candidate. Fabrication and energization remain on hold.**

This revision integrates edge control, isolated metering, post-switch AC-presence feedback and an independent thermal permission latch on a 100 × 85 mm, four-layer board. It retains a separate 12 × 12 mm thermal pickup head and in-enclosure main protection components. The proposal is a single 220 VAC ±10% socket platform with commissioned load profiles, not a universal plug-hole adapter or an unconditional 16 A motor-switching rating.

## Open these files first

- `integrated.kicad_pro`, `integrated.kicad_sch`, `integrated.kicad_pcb`: editable native project
- `exports/schematic.pdf`: six readable functional/assembly sheets
- `electrical_bom.csv` and `electrical_manifest.json`: numbered pins, real candidates and primary-source links
- `ELECTRICAL_SOURCE.md`: circuit and interface definition
- `POWER_CURRENT_REVIEW.md`: current paths, copper-loss calculations and fault limits
- `RAIL_BUDGET.md`: the IRM-10-5 supply reservation and temperature derating
- `validation/final_summary.json`: current board-hashed verification results

The final main board has **101 electrical items plus four mounting footprints**. Of those electrical items, 99 have physical component bodies and two are zero-height test pads. There are 321 unique numbered main-board pad keys. The full six-sheet assembly graph has 348 numbered terminals, including the remote head, harness models and off-board protection.

## What is implemented

- ESP32-C3-WROOM-02U, external antenna connection, programming/boot controls, local button, status LED and polled TMP102 board temperature
- IRM-10-5 isolated 5 V supply and AP63203 3.3 V buck; conservative concurrent reservation 3.885 W, with manufacturer derating kept explicit
- Four-terminal 1 mΩ shunt, graded voltage divider, ATM90E26, 8.192 MHz oscillator, ISO6741 SPI isolation and an R05CT isolated supply for the mains-referenced metering domain
- ACPL-K376 post-switch AC-presence detector; this reports voltage presence, not a certified absence-of-voltage indication or mechanical contact position
- Remote TMP302 threshold sensor, power supervisor, set-dominant hardware trip behavior, local physical rearm edge and independent coil-supply gating
- Defined main fuse → thermal link → protected line → shunt → relay → output path, plus continuous unswitched PE outside the PCB
- Fully connected four-layer copper, an isolated logic return plane, mechanical hole keepouts and modeled through-hole lead reserves

`HOT_GND` is **line potential**, never PE or isolated logic ground. The main fuse is SHF 8020.5080 with two CQP 8040.0003 clips on a retained insulating carrier. F501 is a separate 1 A auxiliary-supply fuse. The thermal link responds to temperature; it is not an overcurrent fuse. There is no active current-limiting circuit. The software reference does not establish an independent, commissioned current-duration trip.

## Verification and its boundary

The canonical results are `final_drc.rpt`, `final_erc.rpt`, `final_pin_audit.json`, `final_isolation.json` and `final_source_graph.json` under `validation/`. Historical intermediate results are retained in Git; only current canonical reports are kept in the working tree.

- Native DRC: zero violations, zero unconnected items, zero footprint errors
- ERC: zero errors and zero warnings
- Independent schematic-to-PCB pin comparison: all 321 main-board keys match
- Independent projected isolation audit: includes all copper layers, unused isolator pins and the complete conservative ground-plane outline; minimum component land gap 8.10 mm; routed copper/plane targets at least 8.4 mm
- Negative controls: a synthetic 6 mm gap is rejected by the supported KiCad rule, and a shifted hot pad is rejected by the independent checker
- Rebuild: placement/net geometry is checked before the saved copper recipe is replayed; no undocumented autorouter state is required

**These are digital checks, not manufactured insulation or current ratings.** The 8.10 mm component-land minimum has only 0.10 mm nominal reserve above the preliminary 8 mm rule. Finished land geometry, solder spread, contamination, creepage, material group, altitude, dielectric construction and measurement tolerances still require a qualified insulation design review. The 2.5 mm open-contact and 3 mm neutral functional rules are preliminary engineering constraints, not a standards-compliance claim.

A negative-control investigation found that earlier JavaScript-style `NetName.startsWith(...)` conditions were not enforced by KiCad. This revision uses supported wildcard comparisons and records both the failing old control and corrected control. The frozen EVT-A baseline was not rewritten; see `../BASELINE_RULE_LIMITATION.md`.

## Physical exports

- `exports/placement_assembly.step`: 144 valid solids for component/body/lead fit checking
- `exports/integrated_assembly.step`, `.FCStd`, `.obj`: 3133 valid solids including actual native pads, traces and vias
- `exports/component_envelopes.json`: component and lead bounds
- `exports/remote_head_assembled.step`, `.obj`, `.json`: 19 valid head solids in final assembly coordinates, with an explicit proper rigid transform and source hash

Main-board exports use millimetres, centered XY, board bottom at local z=0; the mechanical assembly translates MainB by +11.5 mm in Z. The HeadB export is already in assembly coordinates and must not receive that translation. Its pickup copper face is at z=43.5 mm. Copper is raised/colored for inspection; solder mask/tenting and detailed manufacturer body geometry are not qualified by the visualization. Native KiCad copper and plane files remain authoritative.

## Required release gates

1. Confirm the applicable plug/socket standard, market, altitude, insulation class and actual 198–242 VAC operating requirement. The 264 VAC calculation point is measurement headroom only.
2. Obtain actual prospective fault current, upstream breaker curve and fuse total-clearing data. SHF's stated 760 A²s is typical **melting** I²t at 10× rated current, not an upper bound on total let-through. Qualify every trace, via, shunt, terminal, collector, wire and joint accordingly.
3. Test enclosed 16 A temperature rise and short-circuit containment. The copper-loss model and 70 µm outer-copper proposal are not a finished-board current rating. Verify plating, current sharing, solder joints, fuse-clip retention and enclosure heat.
4. Obtain the intended load's steady current, locked-rotor/inrush waveform, repetition rate and switching duty. The relay's resistive rating does not release a 16 A compressor, transformer or capacitive load.
5. Calibrate voltage/current/power/energy with traceable references and signed profile data. Verify shunt polarity, startup checksums, timing, waveform range and overrange behavior. Firmware contract: `../FIRMWARE_CONTRACT.md`.
6. Test thermal pickup lag, threshold spread, pressure/aging of the insulating pad, sensor/pigtail failures, slow power ramps, local rearm and welded contacts. Ideal latch tests cannot prove this physical behavior.
7. Complete EMC/surge/EFT, RF/antenna integration, dielectric/impulse, creepage/clearance, abnormal-operation, mechanical gauge/retention and production reliability testing.
8. Obtain board-house approval of the four-layer stack, 0.20 mm finished signal-via drills, via-in-pad/tenting/fill process and all authored land patterns before any fabrication release.

Power restoration starts de-energized and requires the defined thermal rearm/commissioning sequence. Runtime unknown-load, stale-meter and offline behavior must follow the commissioned policy; they are not universal instructions for abrupt power removal. See the repository's system/network and sensor documentation.

## Rebuild

Use `bash scripts/rebuild.sh --no-geometry` for a source/copper/verification rebuild, or omit the option to regenerate geometry. KiCad 9, its standard libraries, system Python with pcbnew/NumPy, FreeCAD, Inkscape, ReportLab and pypdf are required. The script validates geometry against `routing_recipe.json` before applying copper and then reruns the independent checks. Local vendor-PDF research caches are not required deliverables; official URLs remain in the BOM and authored notes.

## Rear termination integration correction

The corrected front/rear polarity exposed an assembly-level clearance problem that native PCB-domain DRC could not detect. The rear L tail was lowered by the mechanical design, the nearby +5 V and +3.3 V branches were rerouted, and the internal GND plane was recessed. All component placements remain fixed. `validation/rear_termination.json` independently checks the resulting rear metal against native isolated copper, including the conservative entire plane outline. The nominal minimum is 8.5166 mm, versus an 8.4 mm design check. This is not a tolerance-qualified clearance or creepage result. The complete mechanical insulation-domain report remains a separate release gate.
