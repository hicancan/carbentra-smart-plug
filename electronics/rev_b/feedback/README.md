# Rev B isolated post-switch output detector

**Development candidate. Do not fabricate, connect to mains, or treat any signal as a safety indication.** Baseline EVT-A files were not edited. This is a separate, routed Rev B source module, not a certified socket or a release to energize.

## Result and interface

A 35 × 25 × 1.6 mm, two-layer module senses differential voltage at the **actual output socket L and N contacts**, after every switched pole. It uses a full-wave AC-input threshold optocoupler, four protective-impedance resistors and isolated 3.3 V logic. It needs one MCU GPIO capable of observing pulses, plus isolated power and ground. No load current is required.

- J1: L_POST, socket-side line sense only
- J2: N_POST, socket-side neutral sense only
- J3.1: +3V3_ISO; J3.2: GND_ISO; J3.3: OUTPUT_PRESENT_N
- Logic: recurring active-low pulses at twice mains frequency; LOW by itself is not a complete measurement
- Reserve **9 mm above PCB, 3 mm below PCB**, plus mating connector and wire bend/strain-relief space. These are keepout reservations, not a validated complete assembly envelope
- No protective earth conductor or load-current path is routed on this module

`output_feedback.kicad_sch`, `.kicad_pcb`, `.kicad_pro`, `.kicad_dru`, `Feedback.kicad_sym`, `Feedback.pretty/`, `pin_net_manifest.json` and `bom.csv` are the design sources. `exports/` contains schematic and board-review SVG/PNG plus the exported KiCad netlist. `scripts/build_feedback.py` rebuilds the source; `scripts/verify_feedback.py` independently checks connectivity, domain spacing and calculations. No Gerbers or fabrication package is provided.

## Circuit and pin correctness

The implemented signal path is:

L_POST → R1 33 kΩ → R2 33 kΩ → U1 pin 1 (AC1)

N_POST → R4 33 kΩ → R3 33 kΩ → U1 pin 4 (AC2)

U1 is **Broadcom ACPL-K376-560E**. Its internal bridge and input threshold controller feed the optical isolation stage. Pin 8 is isolated VCC, pin 5 isolated GND, pin 6 open-collector output. Pins 2 (DC+), 3 (DC−), and 7 (NC) are intentionally unconnected. R5, 1.8 kΩ, pulls pin 6 to isolated 3.3 V; C1, 100 nF, bypasses its isolated supply. There is no rectifier storage capacitor or mains-to-MCU resistive divider.

The source pin table was visually checked against the manufacturer functional diagram, not inferred from a generic optocoupler symbol. The four resistors are split across both input legs; **neither leg is considered touch-safe or guaranteed neutral**. Their intermediate nodes remain in the primary domain. [Broadcom datasheet, pp. 1–2](https://docs.broadcom.com/doc/AV02-2153EN)

## Why this topology

Three options were compared:

1. **H11AA1 AC phototransistor:** simple and naturally reverse-protected. However, its minimum CTR is 20% at ±10 mA, VCE = 10 V, 25°C. That is not a guarantee at ~1–2 mA, hot, aged, or saturated. At 198 VAC, obtaining 10 mA at the crest requires about 27.85 kΩ or less; at 264 VAC the resistor loss is then approximately 2.50 W before tolerance. Unnecessarily hot for a compact socket. [Vishay H11AA1 datasheet](https://www.vishay.com/docs/83608/h11aa1.pdf)
2. **Discrete 1000 V bridge + VO615A-4 phototransistor:** the 56% minimum CTR at 1 mA is useful, but it is specified at VCE = 5 V and 25°C. Multiplying that CTR into a saturated 3.3 V GPIO interface would overstate the guarantee. A transistor solution requires separate low-VCE/temperature/aging qualification or an appropriately biased comparator design. [Vishay VO615A datasheet](https://www.vishay.com/docs/81753/vo615a.pdf)
3. **Selected ACPL-K376 integrated bridge + threshold optocoupler:** threshold detection occurs before the optical transfer path, so the detector is specified by input threshold limits rather than a guessed CTR minimum. The manufacturer covers −40…105°C and includes 3.3 V operation. The component isolation ratings do not certify this PCB or assembly. [Broadcom datasheet, electrical tables](https://docs.broadcom.com/doc/AV02-2153EN)

This choice still contains a bridge and optocoupler; the bridge is integrated. There is no external diode footprint that can be assembled with the wrong AC/DC pin order.

## Component candidates and footprint basis

| Ref | Candidate | Mechanical/footprint basis |
|---|---|---|
| U1 | ACPL-K376-560E | Manufacturer SSO-8, custom `Feedback:SSO8_ACPL_K376`; body 6.807 ±0.127 × 5.850 ±0.50 mm, max height 3.307 mm; 1.27 mm pin pitch; lead span 11.50 ±0.25 mm |
| R1–R4 | Vishay PR01000103302FA100 | PR01, 33 kΩ, ±1%, 1 W at 70°C, 350 V working-voltage ceiling; custom horizontal 10.16 mm pitch, 0.9 mm drills; max body 6.5 × 2.5 mm; 0.58 ±0.05 mm leads; assembly standoff/lead forming still to qualify |
| R5 | Yageo RC0603FR-071K8L | 1.8 kΩ ±1%, 1608 metric; KiCad 0603 footprint; ordinary isolated-side pullup |
| C1 | Murata GRM188R71C104KA01D | 100 nF ±10%, X7R 16 V, 1608 metric; KiCad 0603 footprint |
| J3 | Samtec TSW-103-07-G-S | 2.54 mm pitch, three 0.635 mm square pins; vertical 1×3 header footprint; 5.84 mm mating post + 2.54 mm body = 8.38 mm nominal above board |
| J1, J2 | Internal insulated wire solder lands | Custom 1.2 mm drill / 2.4 mm copper diameter; **final wire gauge, insulation, anchoring and strain relief remain HOLD**, not a rated detachable mains connector |

U1's custom pads are 1.905 × 0.65 mm, with opposed pad centers 10.745 mm apart. The resulting pad-edge distance is 8.84 mm; the 0.65 mm width follows a practical KiCad SSO-8 land width, wider than the maximum 0.511 mm component lead. The 12.65 mm outer land span follows the manufacturer drawing. A 1 mm wide, 21 mm long routed slot under the package provides extra surface-contamination margin. **This is not permission to reduce air clearance.**

PR01 has a non-flammable coating and documented active/passive flammability tests; it is **not an agency-qualified safety fuse in this use**, and an unspecified benign open-circuit failure is not assumed. Its power/voltage/pulse/load-temperature limits all apply. [Vishay PR01 family datasheet](https://www.vishay.com/docs/28729/pr010203.pdf), [Samtec exact header](https://www.samtec.com/products/tsw-103-07-g-s), [Murata exact capacitor](https://www.murata.com/en-us/products/productdetail?partno=GRM188R71C104KA01D)

## Worst-case electrical calculations

The target is sinusoidal **198–264 VAC, 50/60 Hz**. Distorted/phase-cut waveforms require separate tests. This detector is not an RMS voltmeter. All numbers below are calculations, not bench measurements.

RΣ = 4 × 33 kΩ = 132 kΩ. Initial ±1% gives RΣ,min = 130.68 kΩ and RΣ,max = 133.32 kΩ. High-line peak is 264√2 = 373.35 V; low-line peak is 198√2 = 280.01 V.

Use the component's all-temperature AC-input limits:

- ION,max = 1.56 mA, VON,max = 5.5 V
- IOFF,max = 0.80 mA, VOFF,max = 4.42 V
- ION,min = 0.87 mA, VON,min = 4.23 V
- IOFF,min = 0.43 mA, VOFF,min = 2.87 V

These are instantaneous thresholds. Their extreme combinations are deliberately conservative; correlation is not relied on. [Broadcom datasheet, table 6](https://docs.broadcom.com/doc/AV02-2153EN)

Vsource,on,max = ION,max RΣ,max + VON,max = **213.48 V instantaneous**, or 150.95 VAC if interpreted only as a sine-wave crest threshold. That remains below the 198 VAC crest by 66.54 V. Vsource,off,max = **111.08 V instantaneous**. This broad threshold spread is why amplitude is not reconstructed from a binary reading.

Ignoring the input device's voltage drop gives conservative resistor power/current upper bounds:

- PΣ ≤ VRMS²/RΣ,min = **0.5333 W** at 264 VAC
- Ipeak ≤ √2 VRMS/RΣ,min = **2.857 mA**
- Individual resistor mismatch: Pi ≤ VRMS² Ri/(ΣRj)²; Vi,RMS ≤ VRMS Ri/ΣRj
- Exhaustive ±1% corners give **0.1347 W and 67.00 VRMS** worst for one resistor, not simply PΣ/4
- With one resistor shorted, three remain: **0.7111 W total**, **0.2386 W / 89.18 VRMS** worst remaining part, Ipeak ≤3.809 mA

An additional **±10% resistance analysis envelope** is included in `calculations.json`. This is an engineering allowance, not a manufacturer lifetime guarantee: it accommodates initial 1%, roughly 3% temperature contribution including self-heating, and the 5% endurance-test drift figure with multiplicative headroom. Real mission-life drift, enclosed thermal gradients and pulse damage must be qualified. The margin still supports the target sine-wave range; consult the machine-generated values for exact results. Expected high-line resistor heat is approximately **0.59 W maximum** within that allowance. Do not substitute four unspecified miniature chip resistors.

For one resistor open, a single gap may see the full applied voltage; do not claim the remaining series resistors divide that voltage. An optocoupler input short leaves the series impedance current-limiting; multiple resistor shorts or a carbonized PCB fault are not covered by this simple model. A normal ampere-rated socket fuse may not clear a low-current overheating fault: fuse/impedance coordination and abnormal-condition tests remain mandatory.

### Logic and pulse timing

The 1.8 kΩ pullup sinks at most approximately 1.95 mA with a 3.3 V ±5% rail and −1% resistor. A conservative 100 µA off-leakage allowance leaves at least **2.953 V** at VDD = 3.135 V and Rpullup = 1818 Ω, before host input leakage. Check the actual MCU VIH/VIL specifications, supply tracking and injection-current limits. The datasheet has 3.3 V switching characterization; its 0.4 V static VOL test is stated at VCC = 4.5 V / 4.2 mA, so **the exact 3.3 V low-state margin is still an application verification item**, not silently extrapolated into a new full-temperature guarantee.

For a sinusoid with angular frequency ω, the low pulse width is:

TLOW = [π − asin(VON/Vpeak) − asin(VOFF/Vpeak)] / ω

The high interval around a zero crossing is:

THIGH = [asin(VON/Vpeak) + asin(VOFF/Vpeak)] / ω

At initial tolerance, the shortest calculated low interval across 198–264 VAC is **4.952 ms at 60 Hz**, and the shortest high interval is **1.274 ms**. The wider resistance allowance remains comfortably millisecond-scale. Propagation delays, actual GPIO thresholds and parasitic capacitance shorten or lengthen observed intervals. Use interrupt timestamps or ≥2 ksample/s polling; do not apply a multi-millisecond hardware RC that erases zero-crossing gaps.

Recommended firmware contract:

1. Begin in UNKNOWN after power-up, brownout, reconnect or missing data
2. Accept AC_PRESENT after at least three well-formed pulse periods, expected roughly 8.33/10 ms; provisionally allow 7.5–11.5 ms for qualification, reject isolated sub-0.4 ms spikes and require both levels
3. No valid pulses for 40 ms means **NO_AC_PULSES_DETECTED**, never SAFE, DEAD, ISOLATED or RELAY_OPEN
4. A sustained LOW for 25 ms means **PRESENT_OR_STUCK_LOW / FAULT**, including possible DC/backfeed or a shorted detector output
5. For an OFF command, allow relay release/bounce/settling before comparison (provisional 100 ms); persistent qualified pulses latch an output-present-after-OFF fault, inhibit new ON commands, and request service
6. For an ON command, missing pulses means supply/contact/wiring/sensor fault or unavailable supply; do not repeatedly chatter the relay trying to diagnose it
7. Confirm these provisional windows with the chosen relay and worst-case waveform; software examples alone are not a safety mechanism

## What the signal cannot establish

- A welded contact and a deliberately closed contact can produce the same reading
- An open sense resistor, disconnected wire, dead 3.3 V supply, optocoupler failure or stuck-HIGH GPIO can all hide a live output
- With open neutral, both socket conductors may be live relative to earth while their differential voltage is too small to detect
- Phase-cut voltage, pulses shorter than the detection window, voltage below the threshold, and DC are outside a simple AC-present interpretation
- Capacitive coupling or an RC snubber across an open relay can energize the output enough to produce a real presence indication; that is not necessarily a welded contact
- External backfeed may energize the socket with the relay open
- This is electrically separate feedback from the metering data/relay command, but not a fault-tolerant safety channel, mechanical-position sensor or absence-of-voltage tester

The correct UI phrasing is **“Output voltage detected”**, **“No AC pulses detected”**, or **“Output sensing fault/unknown”**. Never display “Safe to touch” from this module.

## Discharge and stored energy

There is no deliberate primary-side storage capacitor on the detector. The input path loads the output and can discharge some attached capacitance while its internal circuit conducts, but it is nonlinear at low voltage. **No guaranteed discharge time or safe residual voltage is claimed.** A device plugged into the socket, snubber/X capacitor, or backfed circuit may retain energy independently. If discharge is an applicable requirement, design and validate a separate rated bleeder network for the actual capacitance/energy, including its open-circuit fault; never infer compliance from this sensor.

## Independent thermal protection recommendation

These parts belong to the control/load assembly; they are **not fitted on this 35 × 25 mm detector**. The TMP302/latch/coil-feed circuit is implemented separately in `../thermal/`; the series thermal cutoff remains an external integration hold.

1. **Hardware sensor:** TI TMP302BDRLR, SOT-563, 1.6 × 1.6 × 0.6 mm envelope. Pin 1 TRIPSET0 and pin 6 TRIPSET1 to GND select a provisional 70°C trip; pin 4 HYSTSET to 3.3 V gives 10°C hysteresis. Pin 2 GND, pin 5 VS, pin 3 active-low OUT; use 10 kΩ pullup and local 100 nF bypass. Place it at the validated thermal pickup, away from the detector resistor heat. Its ±2°C device accuracy does not bound temperature error between the socket contact and sensor. [TI pin table and application](https://www.ti.com/lit/gpn/TMP302)
2. **Hardware-dominant shutdown:** route the thermal signal to a set-dominant fault latch / coil-enable path as well as the MCU. Power loss or invalid thermal supply must default to relay-disabled. Hold the relay disabled through the sensor startup interval, at least the specified ~35 ms plus chosen margin; qualify power ramps. Do not let firmware override an active trip or automatically recycle power when it cools. A separate pin-correct local-rearm interlock and routed controller/head candidates are now provided in `../thermal/`; their digital checks do not substitute for physical fault tests
3. **One-shot physical interruption:** use a thermally coupled **Sensience MICROTEMP G5-series** line-series thermal fuse; the manufacturer's resistive envelope includes 20 A/277 VAC, unlike a casually chosen 15 A/250 V link. Provisional Tf = 98°C has Th = 83°C and Tm = 410°C; the body is approximately 14.7 × 4.0 mm, with 1.0 mm leads. Exact order variant, the chosen load category, required regional ratings and fuse coordination need supplier confirmation before release. The manufacturer advises keeping continuous operation below Tf −25°C, so Tf98°C is incompatible with a normal 80°C fuse location. A lower trip threshold may be needed after hot-spot testing. [Manufacturer G5 product](https://www.sensience.com/products/microtemp-thermal-fuse-3/), [manufacturer catalog](https://www.sensience.com/wp-content/uploads/2022/12/Microtemp_Catalog.pdf)
4. Mount the thermal fuse against the relevant hottest current-carrying interface through a qualified insulating thermal path, following lead-forming, crimp/weld and heat-sinking instructions. Its metal body is electrically live. Neither a remotely located board sensor nor a software temperature estimate protects a loose socket contact reliably

A thermal latch opening the same relay coil **cannot clear welded load contacts**. The one-shot fuse is a different interruption mechanism but only opens when heat reaches its trigger; an independent rated disconnect/contact mechanism is needed if the requirement is guaranteed removal of output power after a weld at normal temperature. PE remains continuous and unswitched.

## Verification and remaining release holds

Digital checks are in `validation/`:

- All 25 numbered component pins agree between schematic-exported netlist, PCB and manifest; expected no-connects are U1.2, U1.3 and U1.7
- Conservative minimum cross-domain copper separation is **8.795 mm**, including every pad, NC pads, track and via on both copper layers
- A negative control deliberately inserted primary copper closer than 8 mm; the actual KiCad custom rule caught it. Its report is retained, the intentionally invalid board is not
- Final production-candidate ERC/DRC reports are separate from that intentionally failing negative-control report
- Schematic and board-review images are visually inspected; no physical tests or certification tests have run

Remaining holds: complete enclosure/board capture and slot-strength review; insulated harness and strain relief; contamination/altitude/overvoltage-category assumptions; actual PCB CTI/material and applicable product standard; creepage around the entire assembly and wires; surge/EFT/ESD and coordinated protection; resistor hotspot/endurance; 3.3 V logic margins; hot/cold/aged pulse tests; component source authenticity; sensor open/short/power-loss faults; live/neutral reversal/open-neutral/backfeed; snubber leakage and stored energy; real load thermal tests; independent thermal cutout/interlock integration. **Zero digital-rule violations does not close these holds.**
