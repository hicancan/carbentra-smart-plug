# Rev B hardware thermal interlock: local rearm only

**ROUTED DEVELOPMENT CANDIDATES / FABRICATION AND ENERGIZATION HOLD.** The pin-connected circuit has separate 45 × 35 mm controller and 12 × 12 mm sensor-head PCBs, component footprints and a machine-readable manifest. These are digitally checked source boards, not a certified protective circuit or tested thermal assembly. EVT-A was not modified.

## Implemented behavior

The circuit adds independent hardware permission in series with the **5 V relay coil supply**. The existing MCU low-side relay driver still controls ordinary on/off operation, but cannot energize the coil while the thermal permission is cleared.

- Power-up and undervoltage clear the permission latch
- An overtemperature indication asynchronously clears it, regardless of clock/button state
- Cooling alone never rearms the latch
- A fresh **local physical rearm button** press is required after temperature is healthy and the supervisor settling interval finishes
- A button held through power-up, a fault or recovery does not create a fresh clock edge, and cannot automatically rearm after that recovery
- **There is no MCU or remote rearm net and no additional required MCU GPIO**
- Optional state observation is through TP1 (COIL_ARMED) and TP2 (THERMAL_READY), without a host GPIO dependency

This means **every power restoration requires a physical rearm press**. The finished product needs a qualified insulating actuator accessible with the enclosure closed, or it is a service-only arrangement. Opening a mains-connected enclosure to reach this prototype button is not an acceptable user workflow. This circuit does not provide the final button/enclosure safety design. A powered rearm could energize the coil immediately if the ordinary low-side RELAY_CMD is already HIGH; rearm is not a replacement for the system OFF command.

## Exact circuit

### 1. Sensor head

U1 is **TI TMP302BDRLR**, 6-pin SOT-563. Pin 5 takes +3V3_HEAD, pin 2 GND_HEAD, pins 1 and 6 are grounded for a provisional 70°C threshold, and pin 4 is high for 10°C hysteresis. Active-low pin 3 drives THERM_RETURN. R1 is a **10 kΩ pullup at the sensor head**, not at the controller; C1 is 100 nF across its supply. J4 is the sensor-side three-pad **front-SMD pigtail**, with 2.0 × 1.4 mm lands at 2.54 mm pitch and no through holes. The head is installed with its component face toward the rear. Pigtails and components occupy that rear-facing side; reserve 2 mm for wire/strain-relief assembly. The opposite, contact-facing B.Cu side has a fixed **GND_HEAD copper island** bounded by KiCad x=1.2…4.5 mm, y=4.3…6.9 mm, and four 0.3 mm drill / 0.6 mm copper thermal vias at (1.6,4.7), (2.4,4.7), (3.4,4.7), (4.2,4.7). These vias are tented in the source. No live-metal or separate isolated island is introduced. Smoothness, any via-fill/cap requirement, insulating thermal pad, pressure, wire anchoring and thermal lag remain unqualified. The part accuracy is ±2°C, but thermal coupling to the actual socket-contact hot spot is unqualified. [TI TMP302 pin table and configuration](https://www.ti.com/lit/gpn/TMP302)

At the controller, R2 = 100 kΩ pulls THERM_RETURN to GND_ISO; U2, **SN74LVC1G17DBVR**, restores it through a Schmitt buffer. Thus opening the return wire lets the controller input fall LOW. The normal healthy head pullup drives it HIGH. U2's output HEALTH_VALID drives U3 MR. The buffer prevents U3's internal MR pullup from defeating the return-wire pulldown.

**Coverage is limited:** return-wire open, head supply-wire open, and a return short to ground are intended to trip. A disconnected sensor ground, a return short to the supply, an internal sensor stuck-HIGH failure or some connector bridges may look healthy. This is not a fully supervised safety sensor loop. W1 and W2 are schematic-only harness conductor models, not BOM resistors.

### 2. Voltage supervision and settling

U3 is **TPS3808G30DBVR**, not G33. SOT-23-6 pin map: 1 RESET_N, 2 GND, 3 MR, 4 CT, 5 SENSE, 6 VDD. VDD and SENSE connect to isolated 3.3 V. HEALTH_VALID drives MR. R3 = 100 kΩ connects CT to VDD, selecting the manufacturer's **180–420 ms** specified delay. R4 = 10 kΩ pulls RESET_N high on READY_RAW. U6, SN74LVC1G17DBVR, buffers READY_RAW to THERMAL_READY with a fast Schmitt-trigger edge and local 100 nF bypass C7. This avoids presenting a slow open-drain RC rising edge directly to the flip-flop CLEAR input. LOW means not ready.

The G30 nominal falling threshold is 2.79 V. Including ±1.5% threshold accuracy and 2.5% maximum hysteresis gives a conservative release ceiling of **2.9016 V**, below the assumed 3.3 V −5% = 3.135 V rail. G33 can require more than 3.135 V at the upper threshold/hysteresis corner, so it was rejected for this rail assumption. The minimum 180 ms delay exceeds the sensor's 35 ms startup interval by 145 ms. [TI TPS3808 datasheet, G30 threshold, pin table and delay specifications](https://www.ti.com/lit/ds/symlink/tps3808.pdf)

A thermal fault drives MR LOW and asserts RESET_N without waiting for the release timer. Any fault during a pending settling period restarts the delay. The delay controls when rearming becomes possible; it does not itself energize the relay.

### 3. Trip-dominant latch

U4 is **SN74LVC1G74DCUR**, VSSOP-8:

| Pin | Connection |
|---|---|
| 1 CLK | REARM_CLK from U5 |
| 2 D | +3V3_ISO |
| 3 Q_N | no connection |
| 4 GND | GND_ISO |
| 5 Q | COIL_ARMED |
| 6 CLR_N | THERMAL_READY |
| 7 PRE_N | +3V3_ISO, permanently inactive |
| 8 VCC | +3V3_ISO |

The asynchronous CLEAR is the only asynchronous state-changing input in use. This avoids an SR latch's forbidden simultaneous set/reset combination. While CLEAR is LOW, Q is LOW even if the button generates clock edges. With CLEAR HIGH, a rising clock edge captures D = HIGH; otherwise the prior state is retained. A live fault also physically disables the series transistor gate independently of Q. [TI flip-flop datasheet and truth table](https://www.ti.com/lit/ds/symlink/sn74lvc1g74.pdf)

SW1, Omron B3F-1000, is the only rearm input. R5 = 1 kΩ limits charge into C5 = 100 nF; R7 = 100 kΩ discharges the node. U5, another SN74LVC1G17DBVR, converts the RC level to a clean clock transition. Pressed RC time constant is about 0.099 ms and released time constant is 10 ms. This is edge conditioning, not a certified debounce algorithm; repeated bounce clocks after a valid press merely capture the same HIGH. Release the button for at least 50 ms before a new deliberate press.

**Do not AND the clock with THERMAL_READY.** That would create a clock edge when a fault clears while the button is held, causing automatic rearm. The implemented circuit gates the asynchronous clear and the coil feed instead. The digital model tests that distinction.

### 4. Physical coil-feed interlock

Q1 is **AO3401A P-channel MOSFET**: pin 2 source to +5V_ISO, pin 3 drain to COIL_5V, pin 1 gate to COIL_GATE. R9 = 47 kΩ pulls its gate back to its source, the default OFF condition.

Q2 and Q3 are **Nexperia MMBT3904,215** NPNs, pin 1 base, pin 2 emitter, pin 3 collector. They form a series gate sink:

COIL_GATE → Q2 collector; Q2 emitter → Q3 collector; Q3 emitter → GND_ISO

Q2 base is driven by COIL_ARMED through 10 kΩ with a 100 kΩ base-emitter resistor. Q3 base is driven by THERMAL_READY through 47 kΩ with a 100 kΩ base-emitter resistor. Both stages must conduct to pull the PMOS gate low. Therefore forcing/sticking the logic latch Q HIGH does not bypass an actively LOW thermal/power-ready signal in the ideal functional model. [AO3401A datasheet](https://www.aosmd.com/res/data_sheets/AO3401A.pdf), [MMBT3904 datasheet](https://assets.nexperia.com/documents/data-sheet/MMBT3904.pdf)

Assume coil load ≤150 mA and +5 V ±5% for this candidate. Q1's 85 mΩ maximum specified at VGS = −2.5 V gives only 12.75 mV drop and 1.913 mW dissipation at 150 mA, at the specified test temperature; hot RDS(on), actual gate swing and release transients still need testing. The gate sink only needs ≤5.25/46.53 kΩ = **112.8 µA** steady-state. These are coil-driver calculations, not socket-load-current ratings.

**Integration change is mandatory:** J1.4 (COIL_5V) replaces the relay coil's old +5 V feed. The coil flyback diode's cathode must also connect to COIL_5V, with its anode at the existing low-side coil node. Otherwise the original wiring may bypass the intended current-decay loop or couple transients into the ungated rail. The existing low-side RELAY_CMD path remains. No load-current conductor is connected to this interlock PCB.

## Source and interfaces

- `thermal_interlock.kicad_sch`, `.kicad_pro`, `Thermal.kicad_sym`, `sym-lib-table`: KiCad source with embedded symbols
- `pin_net_manifest.json`: exact pins/nets, expected package footprints, normal supply/load assumptions
- `bom.csv`: component candidates; W1/W2 wire models excluded
- `exports/thermal.net`: actual KiCad-exported netlist
- `exports/thermal_interlock.svg` and `.png`: review drawing
- `scripts/build_thermal.py`: deterministic source rebuild
- `thermal_controller.kicad_pcb` / `thermal_sensor.kicad_pcb`: routed low-voltage PCB candidates
- `scripts/build_boards.py` and `routing_recipe.py`: physical source generation and deterministic replay of verified controller copper; `controller_route_recipe.json` is the checked routing source. The search/cleanup scripts are retained only as development tools
- `scripts/verify_thermal.py`: 94 schematic pins, both PCB pin maps, 13 ideal logic tests and DC calculations
- `scripts/rebuild.sh`: complete build/check sequence; fails if final digital verification fails

The four-wire host connection is J1.1 +5V_ISO, J1.2 +3V3_ISO, J1.3 GND_ISO, J1.4 COIL_5V. These map respectively to main controller J3 pins 7, 1, 11 and 10. There is no separate coil-feed connector. Sensor harness: 3V3, GND, THERM_RETURN. TP1 and TP2 are test points only. All electrical connections here are in the isolated low-voltage domain; maintaining isolation from mains at the remote sensor's thermal mounting is a separate mechanical/material requirement.

The routed board outlines are **45 × 35 × 1.6 mm controller** and **12 × 12 × 1.6 mm sensor head**. Reserve 9 mm above / 3 mm below the controller PCB for headers and tails, plus mating/bend space and reset-actuator clearance. The remote head uses **component-side SMD pigtails**: in the CAD local frame reserve **2 mm on the component side** and a provisional **0.1 mm copper/mask surface allowance on the opposite contact side**, then rotate the head 180° about local Y for the proposed installation. No solder or wire protrusion is permitted on the contact side. C1 is 0.9 mm high and U1 0.6 mm high, both facing the rear; the head must not be modeled as a bare 0.6 mm package. The captive insulating pad and supporting fixture bear on the smooth PCB backside, not the sensor case. Process qualification is still required. `exports/*_envelope.step`, `.FCStd` and `*_envelopes.json` provide simplified source-based package envelopes, not detailed vendor solids or completed enclosure-fit evidence. The neighboring `feedback/` module is a separate routed PCB.

## Checks and limits

Final checks show ERC 0 errors/warnings and DRC 0 violations / 0 unconnected pads on both boards. The controller contains 29 footprints and the head 4; all 94 logical pins match the schematic/manifest, with duplicate switch pads checked separately. The physical rules explicitly permit 0.15 mm isolated-LV fine-pitch clearance. No mains may be brought onto either thermal board. Independent checks compare the exported netlist to every manifest pin, separately assert the manufacturer-critical U3/U4/Q1 pin maps, and verify that no MCU rearm net remains. The ideal state tests include startup, held button, hot reset attempts, simultaneous fault/reset, brownout, repeated settling interruption, return-open fault input, stale-high Q, and preserved dependence on ordinary RELAY_CMD.

The DC calculations also include input leakage: the healthy sensor return is at least approximately **2.799 V** under the selected 3.3 V/resistor/input-leakage assumptions; an opened return stays at or below **0.505 V** with 5 µA worst input leakage. READY_RAW remains at least 3.0845 V with 5 µA buffer input leakage. U6 drives THERMAL_READY; its 100 µA output-load specification gives VOH ≥ VCC −0.1 V, while the connected base-resistor and CLEAR loads stay below that current under the stated assumptions. These values depend on the assumed input leakage, clean PCB and correct harness. They are not test evidence for fault coverage of an arbitrary cable or contaminated assembly.

### Power-up qualification is still open

The intended power-up state is OFF, and digital behavior after the parts enter their specified supply range is checked. **No analog supply-ramp test or transistor/SPICE simulation has established a guaranteed absence of a brief coil pulse at every sub-threshold voltage or supply ordering.** TPS3808's low-voltage reset guarantee depends on pullup loading and ramp conditions; do not extend its 15 µA VPOR test to this 10 kΩ pullup without measurement. Test +5 V first, 3.3 V first, slow/non-monotonic 3.3 V, brownouts, temperature corners and button held through all of them. The source is not released until default-OFF is verified at the actual coil/driver for these cases. Also qualify flip-flop clear recovery timing, RC bounce near the ready transition and the actual hot/cold Schmitt thresholds.

Other holds: physical board/assembly/EMC qualification; sensor thermal contact and insulation; actual relay inrush/hold/release characteristics; power-loss decay; transistor leakage and single faults; reset actuator access; harness open/short combinations; R/C drift; protection of the supply and wiring; fault response at the actual hottest socket/terminal. A shorted Q1 or some sensing faults can defeat this single-channel circuit. It is not a safety-certified or single-fault-tolerant channel.

## Physical thermal cutoff remains separate

A coil-feed interlock **cannot open welded load contacts**. Retain a separately thermally coupled, qualified series thermal cutoff in the load-line path. The neighboring feedback report identifies the MICROTEMP G5 family and provisional Tf98°C selection for supplier/load/thermal validation. No exact regional certification, lifetime or fuse coordination is claimed here. Even a thermal cutoff only interrupts after its thermal trigger is reached; guaranteed disconnection on a cold welded relay requires an independent rated interruption mechanism. PE remains continuous and unswitched.

## Proposed mechanics transform

TMP302 center is KiCad (3.4,6.0) mm on the 12×12 board, or (−2.6,0) relative to board center. A 180° local-Y rotation maps that to (+2.6,0). Therefore a board center at global (−16.6,−7) gives sensor center (−14,−7). With the contact-facing PCB backside at z=43.5 mm, the component face is z=41.9 mm and parts/wires extend rearward from there. This transform confirms geometry only, not measured coupling or electrical insulation.
