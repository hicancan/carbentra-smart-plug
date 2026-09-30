# CarbonMirror electronic development release

## What exists

Editable KiCad 9 schematic and two-layer 72×68 mm PCB; upstream-symbol-derived pin geometry; 33 placed electrical components plus 4 mounting holes (37 footprints); real net assignments; fully connected isolated low-voltage routing (digital connectivity only); true KiCad ERC/DRC reports; BOM candidate sources; board/package STEP, FreeCAD and OBJ; regenerated PDF/SVG review drawings. This is a **development source release with FABRICATION HOLD**, not a finished appliance circuit or a safe prototype to energize.

Main controller: ESP32-C3-WROOM-02U-N4 with external antenna connector, 5 V isolated supply candidate, 3.3 V synchronous buck, relay MOSFET/flyback network and digital board temperature sensor, physical local pushbutton and status LED. GPIO 18/19 are allocated to these controls, so native USB is not available on this revision. Main switching candidate is TE RT314005 5 V coil. Mains input/output/fused-auxiliary nets are intentionally unrouted. The right-hand LV routing region is digitally connected and DRC-checked, not a verified EMC/power integrity layout.

A real external antenna candidate and a mechanical pocket are defined in `PROTECTION_AND_RF.md`. Check module integration approvals and qualify range with enclosure/contact metal. The MCU variant is 02U, with an external antenna.

## Files

- `carbonmirror.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `.kicad_dru`: editable source and preliminary constraints
- `CarbonMirror.kicad_sym`, `sym-lib-table`: local symbols, flattened from installed KiCad library for portability
- `circuit_manifest.json`: machine-readable pins, nets, placements and schematic positions
- `bom.csv`: candidates, NOT a purchase-approved BOM; passives require precise grade/voltage/package selection
- `METERING_DESIGN.md`: substantive isolated metering boundary, pin map and sizing; daughterboard NOT implemented
- `validation/`: actual ERC, DRC, routing and geometric validation outputs
- `exports/`: review-only models/drawings
- `scripts/build_electronics.py`: regenerate source (overwrites board routing)
- `scripts/route_lv.py`: attempt LV routing, always follow with real DRC
- `scripts/export_geometry.py`: nominal package envelopes + board/footprint pad visualization

## Functional and power assumptions

IRM-03-5 candidate supplies 5 V/0.6 A. A 0.403 W relay coil consumes about 81 mA. An assumed 0.5 A peak 3.3 V controller load at 85% buck efficiency draws 388 mA from 5 V, leaving about 131 mA before other loads and supply derating. This is a preliminary budget, not measured. Include metering isolation power and all transients before final selection; verify rail dips during simultaneous radio transmission/relay actuation. Buck capacitor effective capacitance must account for DC bias, and high-current loop/switch-node layout requires review.

AP63203 pins: 1 FB → 3.3 V; 2 EN → 5 V; 3 IN → 5 V; 4 GND; 5 SW; 6 BST. Q1 is AO3400A, with manufacturer maximum RDS(on) of 48 mΩ at 2.5 V gate drive. Its pins are 1 gate, 2 source to ground, 3 drain to coil-low. D1 cathode connects to 5 V and anode to coil-low. R2 holds the gate low when the MCU is high-impedance; it is not an independent safety channel. Relay contact 11 is common, 14 is normally open, and 12 is externally unused but remains a hazardous live terminal when the relay is de-energized; it is assigned L_NC_UNUSED for clearance checking. A welded contact cannot be made safe by firmware.

Cold boot / loss of control power de-energizes this monostable relay. Runtime unknown-load handling is monitor-only; stale data rejects new automatic commands and holds the commissioned state, as specified in the system reference model. Hardware fault interruption, watchdog policy and power-restoration behavior must be commissioned by load category. This board does not implement a universal abrupt shutdown policy.

## Mains and PE

Target: 220 V nominal, 16 A-class single polarized socket. Actual continuous current, branch protection, terminal rating, contact category and operating temperature remain unqualified. **16 A resistive relay rating does not establish air-conditioner/compressor/motor, transformer or capacitive-inrush capability.** Profile software cannot uprate contacts or copper. Unknown loads are monitor-only for automatic energy management; known load categories still require validated hardware limits.

J1, J2 and J5 use Phoenix MKDS 3/2-5.08, part 1711725, with the matching KiCad footprint. Its 24 A nominal rating is a component rating, not this product's released continuous-current rating. Confirm the final conductor, torque, support, temperature rise and strain relief. High-current copper is absent: copper weight, width, neck-downs, solder joints and fault let-through must be engineered before routing. Do not bridge the airwires and energize.

Real main/auxiliary fuse and independent thermal-cutoff candidates are now dimensioned in `PROTECTION_AND_RF.md` and allocated mechanically; their electrical/harness integration and coordination are not validated. Surge network and any required snubber remain incomplete. They require ratings, layout, failure-mode analysis and system-level testing. A fuse is not an over-temperature sensor; a MOV alone is not complete surge protection.

PE bypasses this PCB in an uninterrupted stamped/wired protective path and must never be switched, fused or routed through the MCU ground. Mechanical PE continuity solids are not proof of actual earth-bond resistance, retention or contact force. Never assume N is safe to touch; polarity/reversal fault analysis and all-pole disconnection requirements depend on final product category.

## Review gates before any hardware build

- [ ] Choose target jurisdiction, plug/socket dimensional standard, accessible-part class, temperature range and required compliance tests
- [ ] Complete all mains/protection/metrology circuits and independent thermal safety; produce fault tree and critical-component list
- [ ] Resolve all KiCad unconnected nets and DRC violations without suppressing safety failures
- [ ] Verify every manufacturer pin/footprint drawing, exact suffix, BOM source and symbol connectivity independently
- [ ] Confirm required clearance/creepage from applicable standards; 8 mm rule is an explicitly preliminary engineering target, not a compliance conclusion
- [ ] Validate all copper currents/temperature rises, conductor/terminal retention, PE bond and short-circuit withstand
- [ ] Complete external antenna and metering daughterboard mechanical allocations, wiring paths, connectors and controls
- [ ] Test surge/EFT/ESD/EMI, dielectric/impulse, leakage, abnormal temperature, relay endurance and welded-contact behavior in a qualified lab
- [ ] Verify watchdog, brownout, cold-boot de-energization, stale-data command rejection, offline commissioned-state hold and secure signed firmware behavior
- [ ] Release only after independent electrical/safety review and documented manufacturer acceptance

No Gerber/drill set is supplied because it would misleadingly imply fabrication readiness. Reports may be clean in one domain while the design remains incomplete and unsafe to power.


## Final digital verification

ERC: **0 errors, 0 warnings**. PCB DRC: **0 geometric violations**, **0 low-voltage airwires**, **9 intentional mains-domain airwires**. All 104 assigned pins match the exported schematic netlist and PCB pads. See `validation/final_summary.json` and the complete, unfiltered reports. DRC success does not remove fabrication hold: the mains circuit remains physically incomplete and the metering daughterboard is not implemented.

The final board has 729 routed segments, 85 vias and 2 ground zones. These establish digital connectivity, not safe current capacity, EMC performance, transient integrity, or protection behavior. No embedded firmware has been flashed or exercised on hardware.

KiCad library symbol geometry is attributed to the KiCad Community under its library licence and design exception; see `KICAD_LIBRARY_LICENSE.txt`.


## Rebuild and system interfaces

Run `bash scripts/rebuild.sh` with KiCad 9 and its Python bindings installed. It regenerates placement and schematic, checks fixed geometry, then replays the reviewed completed-LV copper recipe. Do not rerun the experimental autorouting helpers on the finished board. Exporting package STEP/OBJ also requires FreeCAD Python; `scripts/export_geometry.py` handles it.

For the Wi-Fi/BLE deployment boundary, sensor ownership and exact runtime unknown/stale-data behavior, see [wireless networking and sensors](../docs/system/network-and-sensors.md) and [system requirements](../docs/system/README.md). The PCB includes board temperature sensing, not a complete hot-contact telemetry path. Independent relay/output-state feedback and the metering daughterboard remain incomplete.
