# Rev B metering daughterboard

**Development candidate. Do not fabricate for energization or connect to mains.** This revision contains a genuine schematic and fully connected PCB candidate, including the load-current shunt and both isolation barriers. Electrical continuity and DRC do not establish safety, measurement accuracy or manufacturing readiness.

## What is implemented

- 39 electrical components and four M2 mounting holes, 75 × 45 × 1.6 mm board
- ATM90E26-YU, calibrated L-only SPI metering, 8.192 MHz crystal and specified decoupling/reset/filter networks
- Bourns CSS4J-4026R-1L00FE four-terminal 1 mΩ shunt with separate force and sense pads
- Four 249 kΩ precision divider resistors, 1 kΩ lower leg and matched voltage filters
- TI ISO6741DWR default-high reinforced SPI isolation candidate
- RECOM R05CT05S-R configured for isolated 3.3 V; hot ground is deliberately connected to protected line
- Explicit 8 mm HOT-to-ISO copper rule and 3 mm neutral-sense-to-active-hot-circuit rule
- Two separated ground pours; no ground or copper plane crosses the isolation barrier

Native sources: `meter.kicad_sch`, `meter.kicad_pcb`, `meter.kicad_pro`, `meter.kicad_dru`. `circuit_manifest.json` and `bom.csv` hold pin-level design intent and sourced component candidates. `exports/meter.pdf` is the grouped schematic. STEP/FCStd/OBJ are nominal package-envelope and actual trace/via inspection models; they are not vendor detailed manufacturing solids.

## Interfaces and polarity

J1 pin2 receives the externally fused/thermally protected line. J1 pin1 supplies the relay common through the shunt. **This connector intentionally uses pin2 as the input; do not assume pin1 is input.** J2 pin1 is neutral voltage sense; J2 pin2 is unused and must not become a convenience load-current return. Neutral load current remains in the dedicated main power path.

J3 is an isolated 8-pin interface: 1=3V3, 2=GND, 3=SCLK, 4=MOSI, 5=MISO, 6=CS, 7=5V, 8=GND. The separate controller revision uses a combined 2×6 harness with these first eight logical pins and additional feedback/interlock signals. Do not connect matching physical header row positions without the harness drawing.

Hot reference is upstream line. I1P senses the downstream negative shunt drop; I1N senses upstream potential. Voltage VP samples neutral relative to upstream line, so both voltage/current polarity are inverted together and positive consumed active power is expected. Verify sign with a known resistive reference before enabling commissioning. A mistaken Kelvin lead swap must fail commissioning, not be hidden automatically.

## Layout/manufacturing assumptions

The stackup explicitly requests nominal 70 µm copper per side and a 1.6 mm finished board. The two force routes use 4.8 mm top copper, with component-pad necks and solder joints requiring thermal verification. Small signal routing uses 0.15 mm minimum clearance and 0.20 mm finished drills/0.45 mm lands at the smallest vias. Some vias lie in SMD pads: filled/capped via-in-pad processing or a reviewed escape-layout revision is required. Do not issue untreated through-vias under solderable pads.

The custom ISO6741 footprint moves lands outward to provide an 8.1 mm opposite-pad gap. The RECOM land pattern uses the manufacturer's HV option. Assembly solder-joint geometry must be reviewed against actual lead tolerances and stencil. The Bourns footprint uses separate force rectangles and sense tabs based on the published land-pattern dimensions; optional inward sense-routing extensions are omitted. First-article land-pattern verification remains mandatory.

8 mm is a design target, not a declaration of conformity. Applicable product standard, pollution degree, overvoltage category, material group, altitude, working voltage, enclosure barriers, conductive fasteners and wire routing must be independently assessed. Reinforced component ratings do not automatically qualify the board or enclosure.

The oscillator nets currently use multiple layers. Startup margin, drive level, effective crystal load and immunity near the converter need measurement; the 27 pF capacitors assume approximately 4.5 pF total stray loading for an 18 pF crystal. No measured clock or EMC claim is made.

## Validation and remaining gates

Actual KiCad reports are in `validation/`. `net_pin_consistency.json` checks every assigned schematic pin against the exported netlist and PCB; this catches accidental graphical wire joins. `geometry.json` checks model shape validity. The native board is authoritative; no unrouted airwire is represented as a trace in the model.

Required before energization: qualified mains protection coordination, prospective short-circuit current and fuse I²t, shunt fault-pulse/solder survival, all conductor/terminal temperature rises, insulation tests, leakage/touch-current and creepage review, EMI/surge/EFT tests, calibrated metering validation, mechanical harness/lead clearances and formal electrical sign-off. The standard meter cannot interrupt a short circuit and may saturate during appliance inrush. Output-voltage feedback and thermal interruption are separate Rev B boards.

See `../FIRMWARE_CONTRACT.md` for the verified register protocol and calibration-required startup path. No calibration values, firmware commissioning or physical measurements are fabricated here.
