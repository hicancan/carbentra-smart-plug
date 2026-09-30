# CARBENTRA · CM-S16-EVT-B electrical source

**Development candidate. No fabrication, energization, product-rating or certification release.** This document defines the consolidated electrical source and its physical-board boundaries.

## Files and structure

Open `integrated.kicad_sch`. It is the overview for five functional/assembly child sheets:

1. `integrated_controller.kicad_sch`: isolated supply, 3.3 V rail, ESP32-C3, relay/driver, board temperature and local controls
2. `integrated_meter.kicad_sch`: Kelvin current shunt, voltage divider, ATM90E26, SPI isolation and hot-side isolated power
3. `integrated_feedback.kicad_sch`: independently isolated post-switch AC-presence detector
4. `integrated_thermal.kicad_sch`: hardware trip latch/coil permission and the separate remote sensor head
5. `integrated_assembly.kicad_sch`: off-board main fuse, independent thermal link, custom plug/socket contacts and uninterrupted PE

Global net names connect these sheets electrically. The hierarchy does not imply four daughterboards: the placement target is the integrated 100 × 85 mm main board, except the explicitly designated remote head. F501 and the powered oscillator with its bypass capacitor are drawn on the overview.

`electrical_manifest.json` is schema version 1. Each `components[]` entry carries its new reference, original module/folder/reference, source symbol, exact numbered pin nets, original pins/net mapping, symbol-pin geometry, footprint, MPN, source URL, candidate height and physical-board designation. References use offsets 100/200/300/400 for controller/meter/feedback/thermal; F501 is new.

- `board_designation == "integrated"`: 101 main-board parts
- `board_designation == "remote_sensor"`: U401, R401, C401 and J404, on the 12 × 12 mm head
- `board_designation == "harness_model"`: W401/W402, schematic-only conductor models, not PCB/BOM parts

- `board_designation == "off_board_assembly"`: F601, TF601, J601 and J602; four internal off-main-board assemblies, `on_board=false`

There are 109 electrical/physical component entries plus the two harness models. The fuse holder is recorded as F601’s mechanical accessory, not an additional electrical device. Symbol libraries and `sym-lib-table` are local to this source. Custom footprint libraries are registered/created by the PCB owner; this schematic generator never overwrites the PCB or existing project configuration.

## Explicit integration changes

- Input terminal J201.1 is **HOT_GND, protected line potential**; J201.2 is HOT_N. HOT_GND is never protective earth or isolated logic ground
- RS201 shunt feeds HOT_LOAD into K101 common pin 11; the NO contact pin 14 feeds HOT_SWITCHED and J102.1. J102.2 is HOT_N
- F501 connects HOT_GND to HOT_AUX_FUSED for PS101; the separate F601 main load fuse and TF601 physical series thermal cutoff are explicitly drawn on the assembly sheet
- The coil supply is **COIL_5V**, coming from thermal PMOS Q401.3. Both K101.A1 and flyback diode D101.1 connect to this gated rail; the original low-side driver remains
- Feedback uses HOT_SWITCHED/HOT_N and its own HOT_FB_* intermediate nets; U301.6 and MCU U101.15 share OUTPUT_PRESENT_N
- Metering's isolated interface shares SPI_SCLK/MOSI/MISO/CS, +3V3_ISO, +5V_ISO and GND_ISO with the controller. Meter HOT_* nets remain mains referenced
- Thermal private signals use TH_* prefixes. SW401 is the only rearm input. No MCU rearm pin or extra GPIO is introduced
- Unused live-potential relay terminal K101.12 retains canonical HOT_NC. Its overview PWR_FLAG is an ERC naming anchor, not a PCB part or a new supply connection

The removed standalone board connectors are listed in the manifest. The remote-head harness connection remains: J403 is on the main board, J404 is the low-profile head-side SMD pigtail. The source makes their board distinction explicit.

## Terminal, fuse and clock candidates

J102 and J201 use **Phoenix Contact 1868076 / MKDS 5/2-7.62**, with Integrated:MKDS5_2_7p62 footprint, 7.62 mm pitch, 1.3 mm drill and 15.24 × 12.5 × 21.5 mm body allowance. The terminal's nominal/approval-category ratings do not establish the socket assembly's current rating. [Manufacturer data](https://www.phoenixcontact.com/us/products/1868076/pdf)

F501 is **Littelfuse 0215001.MXEP**, 1 A time-lag, 250 VAC candidate, with Integrated:Fuse_215_Axial_P30mm footprint authored by the PCB owner. The operating proposal is **220 VAC ±10% (198–242 VAC), pending confirmation**. **264 VAC remains measurement-analysis headroom only, not a released operating rating.** Interruption capacity, branch coordination, inrush, ambient-temperature derating and exact assembly still require qualification. [Manufacturer 215 datasheet](https://www.littelfuse.com/assetdocs/littelfuse_fuse_215_datasheet.pdf?assetguid=990f7193-d9a2-48e4-b760-2b43514249cf)

Y201 is the configured candidate **ASV-8.192MHZ-LC-S-T**. It replaces the passive crystal only in the integrated design. Pins: 1 OE→HOT_3V3, 2 GND→HOT_GND, 3 OUT→HOT_XIN, 4 VDD→HOT_3V3. ATM90E26 U201.22 remains the clock input; U201.23 OSCO is explicitly NC. CX201 becomes a local 100 nF HOT_3V3/GND bypass; CX202 is removed. The 2.97–3.63 V oscillator supply range covers the stated 3.1–3.5 V isolated module output. The chosen 8.192 MHz configuration has a 10 mA maximum supply-current specification in the applicable frequency band. The exact-frequency part's procurement/orderability is still a gate. [Abracon ASV datasheet](https://abracon.com/Oscillators/ASV.pdf)

The integrated-only current-filter pair R201/R202 uses 100 Ω TNPW0603100RBEEA resistors (0.1%, 25 ppm/K) in 0603 footprints so they can be placed close to the AFE inputs. Their nets are unchanged; the modular meter reference is unchanged. [Vishay TNPW e3](https://www.vishay.com/docs/28758/tnpw_e3.pdf)

## Final remote-head concept

The 12 × 12 mm head mounts with its component face toward the rear. F-side SMD pigtail pads keep solder/wire protrusions off the opposite contact-facing side. The B-side thermal copper island is **GND_HEAD**, the same isolated ground used by TMP302; four tented thermal vias couple it to the sensor-ground region. No live or separate floating thermal island is introduced.

The intended contact is the smooth PCB backside through a captive qualified insulating thermal pad, without force on the TMP302 package. Solder mask is not credited as a safety insulation barrier. Via fill/tenting flatness, pad dielectric behavior under pressure/aging, thermal lag, hot-spot tracking, strain relief and actual temperatures remain unqualified.

TMP302 local center is (3.4, 6.0) mm, or (−2.6, 0) from the head center. The final proper rigid transform is a 180° rotation about local X, then `x_world = x_local + 4.8272413`, `y_world = 1.25 − y_local`, `z_world = 43.465 − z_local` in millimetres. It places the head center at (+10.8272413, −4.75), TMP pickup at (+8.2272413, −4.75), and the outer 35 µm backside copper pickup face at z=43.5. It is not a mirrored PCB. The substrate back is at z=43.465. The explicit matrix, world bounds and source hash are in `exports/remote_head_assembled.json`. These are geometry definitions, not measured thermal-coupling evidence.

## Verification

`validation/independent_schematic_checks.json` records the actual exported netlist comparison:

- 334 numbered component pins match the manifest
- 23 critical PCB/head end-to-end connection assertions pass
- A separate full-assembly export checks all 348 numbered pins, including ten off-board terminals and four harness-model terminals
- PE has exactly J601.3 and J602.3 as nodes, with no PCB node; RAW_L and HOT_TF_IN are also excluded from PCB parts
- Four-pin ASV connection verified; OSCO NC and CX202 removal verified
- No MCU rearm net; the four remote-head parts are explicitly excluded from main-board placement
- Canonical global net names are retained, including HOT_NC

The PCB/head netlist is `exports/integrated.net`. KiCad normally omits `on_board=false` devices; `validation/full_assembly_graph.net` is exported from a temporary validation copy enabling only those flags, without changing canonical source. SVG/PNG review sheets are in `exports/`. The final ERC report, `validation/erc.rpt`, has **0 errors and 0 warnings**, with the custom-footprint libraries resolved. Electrical pin checks do not replace PCB DRC or actual testing.

`feedback/` and `thermal/` contain separately checked modular reference PCBs; those files and EVT-A are not changed by the integration generator. The thermal module's saved routing recipe supports a repeatable clean rebuild. Its ideal logic tests are not proof of every analog power-ramp or component fault. Power-up coil-pulse exclusion, relay release behavior, sensor-loop fault coverage, actual thermal thresholds and physical qualification of the independently drawn load-line cutoff remain release holds.

Neither OUTPUT_PRESENT_N nor the relay command proves the outlet is dead or that contacts physically opened. The thermal coil interlock cannot interrupt welded load contacts. PE is continuous, external and unswitched.

## Full assembly protection

The drawn internal path is J601.1 (rear raw L) → F601 → TF601 → J201.1 / HOT_GND. The actual main-board shunt/relay path then reaches J102.1 and J602.1. Neutral joins J601.2, J201.2, J102.2 and J602.2. PE joins only J601.3 to J602.3 and never passes through the PCB, switching, fusing or software. These pin numbers identify custom mechanical contact wiring, not catalog contact numbering.

### Superseded candidate and why it changed

The former F601 candidate was **0216016.MXP, 16 A fast-acting, 250 VAC**. In the manufacturer’s 216-series datasheet (revision GD.06/16/22), page 2, row 016 gives **750 A at 250 VAC**, 0.004 Ω nominal cold resistance and 462.5 A²s nominal melting integral (tested at 10× rated current). The row has selected *** approval cells; the *** footnote states **“1500A@250Vac for 16A”**. The adjacent + note makes the interruption rating approval-dependent and directs review of the agency certificate. A blanket 1.5 kA claim is therefore not released. Page 1, 8–16 A range, gives these limits for a 16 A part: 24 A / ≥30 min; 33.6 A / ≤30 min; 44 A / 0.04–20 s; 64 A / 0.01–1 s; 160 A / ≤0.03 s. [Littelfuse 216 datasheet](https://www.littelfuse.com/~/media/electronics/datasheets/fuses/littelfuse_fuse_216_datasheet.pdf.pdf)

This is **not an active current limit**: a sustained 24 A fault can persist long enough to overheat inadequately sized contacts/conductors. Prospective fault current, upstream breaker cooperation, interrupting capacity, total clearing rather than melting I²t, conductor/contact/shunt/relay let-through withstand, fuse selectivity and enclosure-temperature derating must be qualified. F501 is the separate 1 A time-delay auxiliary-PSU fuse; it is not the 16 A load fuse. No fuse is drawn in neutral or PE.

The superseded holder was **SCHURTER OGN 0031.8201**, open THT with 22.5 mm pin spacing for a 5×20 mm cartridge. The published rating is 500 VAC, 16 A uncovered, 4 W acceptance at 23°C; covered versions are derated to 10 A in the stated IEC data. Its allowed ambient range is −40…85°C. A carrier/support, soldered connections, strain relief, insulation and finger-safe enclosure installation must be qualified; this is not a free-hanging inline holder and it is not placed on the integrated PCB. [SCHURTER OGN datasheet](https://www.schurter.com/en/datasheet/typ_OGN.pdf)

TF601 is a physically separate **MICROTEMP G5, provisional Tf=110°C** thermal link, with Th=95°C and Tm=225°C at this Tf row; nominal body 14.7×4.0 mm. Exact ordering suffix, regional current/voltage approval, live-case insulation, lead termination process and heat-transfer location remain holds. It must interrupt the physical line path even if the relay contacts weld, but actual response under that fault is not established by this schematic. [Sensience MICROTEMP catalog](https://www.sensience.com/wp-content/uploads/2022/12/Microtemp_Catalog.pdf)

### Current main-fuse candidate after mechanical fit review

F601 now uses **SCHURTER SHF 8020.5080**, 16 A fast, 500 VAC, with **two CQP 8040.0003 silver-plated clips**. The fuse body is 31.8×Ø6.35 mm. Its max130 mV drop at16 A gives a2.08 W dissipation ceiling at the specified rated-current test condition. Its footnote3 specifies1.5 kA interruption at250 VAC/cosφ0.7–0.8 and500 VAC/cosφ0.99–1. The **760 A²s figure is typical melting I²t at10×In**, not total-clearing energy; no downstream-withstand bound is claimed. This is larger than the replaced216’s462.5 A²s, so the substitution does not establish fault selectivity. [SHF manufacturer datasheet](https://www.schurter.com/en/datasheet/typ_SHF_6.3x32.pdf)

The CQP clips explicitly match this cartridge format and carry32 A/600 VAC/DC ratings; the silver version’s ambient range is−55…155°C. Drawing: clip width7.85 mm; height10.3 mm above support and13.9 mm including pins; each clip has two pins7.6±0.1 mm apart, with the complete four-hole pattern outer span34.9±0.3 mm; holes1.8(+0.1/0) mm. Derived clip-center spacing is27.3 mm. The published≤10 mΩ contact resistance test at100 mA is not a promised assembled high-current thermal-rise result. No assembled power-acceptance curve is supplied for the custom carrier. [CQP manufacturer datasheet](https://www.schurter.com/en/datasheet/typ_CQP.pdf)

Mechanics accepted a **45×16×2 mm custom insulating carrier** within the current shell: x−48…−32, z41…43 mm; clip centersY±13.65; pinY±17.45/±9.85; clip topz53.3 and untrimmed pin endsz39.4 mm. Dedicated4×1.2 mm copper collectors carry load current rather than narrow carrier traces. This is a feasible installation candidate with increased clip-current margin; retention, contact heating, dielectric clearances, solder joints, fuse replacement access and50–60°C continuous16 A operation remain physical qualification gates.

The replaced OGN’s full-current graph gives approximately2.8 W acceptance at50°C and2.4 W at60°C, below the216 fuse’s16 A×0.2 V=3.2 W rated-current ceiling. That comparison cannot prove failure of every real sample, but it defeats a guaranteed hot-margin claim and motivates the change. A larger fuse nominal current has **not** been substituted merely to suppress nuisance opening.

## PCB linkage and power-review tools

`scripts/audit_pcb_pins.py` is read-only: it compares the101 integrated footprints and321 numbered pad keys to the actual schematic netlist. H1–H4 are allowed only as explicitly verified unnumbered, unconnected NPTH mechanical footprints. It does not claim routed copper continuity.

`scripts/patch_schematic_paths.py` derives root/child/symbol UUID paths from the actual hierarchy. Default mode writes only a dry-run report. The PCB owner may run it with `--apply` only while routing is paused. It changes only footprint `(path)` fields, proves the parsed document otherwise identical, and rejects concurrent writes. Geometry and nets are never recomputed by this patch.

`RAIL_BUDGET.md` and `validation/rail_budget.json` document the5 V design reservation, separate guaranteed maxima from assumptions, avoid double-counting the hot-island oscillator, and identify module-temperature derating. No full thermal qualification is claimed.

PS101 is now **IRM-10-5** in the integrated source only, using the native IRM-10-5 symbol and Integrated:IRM10_Controller_Candidate footprint. It retains the exact nets and numbered pad coordinates:1N=(0,0),2L=(0,10.75),3−V=(38.5,10.75),4+V=(38.5,2.75) mm. Both official bottom-view case222A drawings agree after top-view mirroring; no geometry or net substitution is needed. The authored footprint variant retains standard IRM-10 real case/pad geometry and relocates review silkscreen/reference artwork; it is registered rather than suppressing the native library-mismatch check. The modular controller remainsIRM-05.

The separate power-current review is in `POWER_CURRENT_REVIEW.md`. Its additive trial and DRC delta do not replace the PCB owner’s final merged DRC. Parent-approved changes never overwrite the live board from the review scripts.
