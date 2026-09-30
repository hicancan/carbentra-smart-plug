# High-current copper and thermal-interlock review

**Result:** the separate power-copper candidate reduces a stated nominal route-resistance model by **28.7%** without moving parts or deleting existing routes. The candidate is an additive development patch, not a fabrication release. The parent owns merging it into the live board and rerunning final DRC.

## Audited source and exact patch

- Native input snapshot hash and all 16 operations: `validation/power_candidate_patch.json`
- Preserved input: `integrated_power_baseline.kicad_pcb`
- Separate trial: `integrated_power_candidate.kicad_pcb`
- Reproduction: `scripts/build_power_candidate.py` (writes these two separate copies, never the master; use --source integrated_power_baseline.kicad_pcb to reproduce the preserved trial after the live master contains the improvement)
- Native DRC: `validation/power_baseline_drc.json`, `power_candidate_drc.json`, and `power_candidate_drc_delta.json`

The DRC delta has **zero added violations**, including no added short or clearance violation. The captured master was undergoing routing edits and had five inherited findings and one unconnected item; that is not a clean final board. In particular, an inherited Kelvin-down/I1P short cannot be dismissed because it is inherited. The parent is correcting its live routing and must verify the final merged result. The trial copied the explicit symmetric 2.5 mm open-contact rule, the 3 mm neutral rule, and the 8 mm hot/isolated rule.

The patch does the following:

1. Widens the four existing 2.4 mm HOT_N segments on B.Cu to 4.8 mm; its existing 4.8 mm trunk stays unchanged
2. Widens HOT_GND’s F.Cu input neck from(28.5,62) to(32.5,62),2.4→4.8 mm
3. Adds a 2.4 mm F.Cu lane between the two K101 COM lands,(49.2,47.5)↔(49.2,55)
4. Adds a 2.4 mm B.Cu lane between the two NO lands,(44.16,47.5)↔(44.16,55)
5. Adds a 2.4 mm B.Cu input-shunt parallel route through(28.5,62),(32.5,62),(35,59.9),(39.15,59.9)
6. Adds six HOT_GND through-vias,0.4 mm drill/0.8 mm land, at y 59.65 and x 36.8,37.5,38.2,38.9,39.6,40.3

The existing PTH terminals/relay lands connect the parallel necks between outer layers. The added shunt-input vias enter force pad 1, not a Kelvin pad. An earlier two-row attempt really shorted the inner Kelvin trace and was rejected; only the checked single row belongs to the patch. The original shunt-output array remains eight 0.4/0.8 mm vias. The final shunt position used is(40,64.5),270°.

### Why the widening is limited

- 5.5 mm neutral copper fails the 3 mm requirement to the switched terminal land;4.8 mm passes in the trial
- Two adjacent relay lanes cannot both become 2.8 mm: their 5.04 mm centers would leave only 2.24 mm copper gap.2.4 mm leaves 2.64 mm track-to-track
- The existing wide NO escape is tapered by the parent near the COM lands; preserving a 2.5 mm functional gap is more important than blindly widening it
- Widening the short switched-output terminal neck on F.Cu conflicts with neighboring neutral sense routing. It was left unchanged
- The wider shunt-output B.Cu route is underneath populated AFE/filter circuitry; a simple full F.Cu mirror would cross existing components/nets. This patch does not pretend that space is free

## Resistance and heating calculation

Use R=ρL/(wt), with 20 °C commercial copper referenceρ=1.7241×10⁻⁸ Ω·m; nominal outer copper 70 µm, inner 35 µm; α≈0.00393/K for sensitivity. These are material/geometry estimates. Etching, actual finished copper and via plating are not verified. The native stackup is a candidate specification, not a supplier coupon measurement. [NIST copper wire tables](https://nvlpubs.nist.gov/nistpubs/Legacy/hb/nbshandbook100.pdf)

Actual selected centerline lengths from the captured native board:

| Main path | Baseline length | Baseline R20 | Candidate equivalent R20 |
|---|---:|---:|---:|
|Input to shunt force 1|11.367 mm|0.789 mΩ|0.408 mΩ|
|Shunt force 4 to far COM pad|30.575 mm|2.296 mΩ including 8-via model|1.911 mΩ|
|Far NO pad to output|23.449 mm|1.939 mΩ|1.554 mΩ|
|Neutral terminal-to-terminal|25.725 mm|2.255 mΩ|1.320 mΩ|
|**Total**|**91.116 mm original trace centerline**|**7.279 mΩ**|**5.193 mΩ**|

The deliberately conservative far-pad model sends 16 A through the full listed serial lengths, including both 7.5 mm inter-pin relay necks. The relay has duplicate physical COM/NO lands and internal conductive paths; their actual current sharing is not measured. Omitting those optional inter-pin lengths gives a useful near-pad alternative, not a rigorous bound on the complete assembly.

| Model at 16 A | Baseline | Candidate |
|---|---:|---:|
|Far-pad case,20 °C copper|1.863 W|1.329 W|
|Near-pad alternative,20 °C copper|1.469 W|1.132 W|
|Far-pad case,60 °C copper|2.156 W|1.538 W|
|Far-pad case,100 °C copper|2.449 W|1.747 W|

These temperatures are imposed **copper temperatures**, not predicted ambient or temperature rise. Loss does not establish ampacity without a heat-transfer model or test. The shunt adds approximately 0.256 W at 16 A for 1 mΩ, before tolerance. Fuse, relay-contact, connector, solder-joint, collector and plug/socket-contact losses are additional. Do not present this table as complete sealed-enclosure heat generation. [Bourns shunt data](https://www.bourns.com/docs/product-datasheets/css4j-4026.pdf)

## Via/current-sharing assumptions

Thin-wall barrel model R=ρh/(Nπdt), h=1.6 mm, finished drill diameter modeled as 0.4 mm. At 20 µm wall plating, the output eight-via array is about 0.137 mΩ; the added six-via array is 0.183 mΩ. At 15/25 µm plating the eight-via result is 0.183/0.110 mΩ. Eight equal vias at 16 A carry 2 A each and dissipate about 35 mW collectively at 20 °C. This small DC number does not prove fault or fatigue endurance.

The input six-via array carries only the modeled parallel-branch fraction; finite barrel resistance is included when calculating that fraction. Actual sharing depends on spreading resistance, via position, solder wetting and neck entry. The 0.7 mm center spacing leaves a nominal 0.3 mm drilled web for 0.4 mm holes; hole tolerance, annular-ring registration and resin integrity need manufacturing review. Require a defined **minimum finished barrel plating**, minimum outer-copper thickness, microsections/coupons and solder-process validation. Do not credit solder-filled holes unless the assembly process actually provides and qualifies them.

## Prefuse branch and fault energy

The actual branch J201.1→F501.1 is 24.618 mm at 2.4 mm width plus 1.897 mm at 1.8 mm:26.515 mm total, about 2.786 mΩ at 20 °C. At 0.1 A normal auxiliary input this is only 28µW. A short anywhere before F501, however, is protected by **F601**, not by F501. Its 1.8 mm taper/input land is a fault-withstand concern even though ordinary dissipation is negligible.

F601’s selected SHF data gives a typical **melting/pre-arcing** integral 760 A²s at 10×In. It is not total-clearing I²t, a guaranteed maximum, or an allowed downstream energy budget. No copper-clearing comparison here assumes otherwise. [SHF datasheet](https://www.schurter.com/en/datasheet/typ_SHF_6.3x32.pdf)

Required closure includes available fault current at the installed outlet, fuse/holder interruption conditions, upstream breaker coordination, actual clearing waveform/integral, wiring and PCB arc behavior, and post-fault insulation/containment. Use E=∫i²R(T)dt only with an actual current/time envelope and a thermal model; steady-state R alone cannot predict copper survival. Parallel vias/traces reduce nominal resistance but do not establish a protective fault-current limit. Higher fuse interruption capacity does not automatically lower let-through energy.

Also qualify relay making/breaking duty for the actual load, including compressor/capacitive inrush. A16 A contact or terminal rating is not blanket 16 A switching authorization for every load category. [TE selected relay](https://www.te.com/en/product-1-1649328-0.html)

## Independent thermal latch

The integrated manifest’s actual pins were independently checked and the 13 pure ideal-logic tests rerun without modifying the frozen thermal reference. Result: **no MCU rearm path**, deliberate SW401 rising-edge rearm only, asynchronous trip priority, no rearm merely from cooling or a held button, and a second live-ready gate in series with the PMOS gate sink. K101.A1 and D101 cathode are both on gated COIL_5 V; there is no intended ungated coil-feed bypass.

This establishes the intended latch logic behavior, **not guaranteed physical fail-safe behavior**. Sub-threshold supply order/ramp behavior, asynchronous recovery timing, transistor faults/leakage, sensor ground-open/return-to-supply faults, actual thermal coupling and relay opening have not been physically qualified. A shorted PMOS or welded relay contacts can defeat the coil channel; TF601 remains an independent physical line-series thermal link. The voltage-presence detector cannot prove a safe dead outlet. [DFF truth table](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf), [supervisor timing](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

Numeric reproduction and exact segment data: `scripts/review_power_paths.py`, `validation/power_path_review.json`. Latch results: `validation/integrated_latch_review.json`.

The separate candidate also passes the independent all-layer projected hot/isolated copper audit: minimum8.10 mm, PS201.9↔PS201.8, with zero projected gaps below8 mm. This is a geometric engineering check, not certification or a dielectric test. Report: `validation/power_candidate_projected_isolation.json`.

## Parent merge verified

The parent merged the additive patch. A separate read-only audit found all16 expected changes exactly once in the live native board, with correct nets, layers, widths and via dimensions. See `validation/power_patch_application_audit.json`; rerun with `scripts/audit_power_patch_applied.py`. This verifies application of the reviewed change, not the full board’s final DRC or physical current rating.
