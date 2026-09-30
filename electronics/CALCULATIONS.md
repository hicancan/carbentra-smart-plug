# Preliminary electrical budget and thermal sensitivities

These calculations use declared assumptions and are not measured performance. They establish design questions, not a permissible operating rating.

## Isolated power budget

At an assumed 0.5 A peak controller load on 3.3 V and 85% buck efficiency:

- Buck input: 3.3 × 0.5 / 0.85 = 1.941 W, or 388 mA at 5 V
- Relay coil candidate: 0.403 W, or about 81 mA at 5 V
- Combined: 2.344 W, leaving 0.656 W of a nominal 3 W supply before other loads and temperature derating

A metering isolator, its isolated DC/DC converter, any external sensor and output transients must be added. Measure voltage dips with radio transmission and relay actuation coincident. A supply nameplate margin does not establish stability or enclosure thermal performance.

## Coil driver and status LED

For 81 mA coil current and AO3400A maximum 48 mΩ at 2.5 V gate drive, ideal conduction loss is 0.081² × 0.048 ≈ 0.315 mW at the specified data-sheet conditions. Gate drive is nominally 3.3 V; account for output-level tolerance, temperature and switching transitions. The flyback diode changes relay release time and must be checked against contact arcing and manufacturer guidance.

For a nominal green LED forward voltage of 2.1 V, the 1 kΩ series resistor gives (3.3 − 2.1)/1000 = 1.2 mA. Actual optical intensity, forward voltage and light-guide coupling remain unmeasured.

## Contact-path heating sensitivity

At 16 A, EACH milliohm in a terminal, relay contact, fuse, solder joint, conductor or socket contact dissipates 0.256 W. For illustration:

| Resistance of one interface | Loss at 16 A |
|---|---|
| 1 mΩ | 0.256 W |
| 5 mΩ | 1.28 W |
| 10 mΩ | 2.56 W |

These are sensitivity values, not estimated actual contact resistance. Measure the assembled path with four-wire methods, then validate temperature rise under worst-case contact force, torque, ageing, ambient temperature and enclosure orientation. Summing several interfaces can dominate the electronics' own heat. The thermal fuse must respond to the actual hazardous hot spot, including transfer delay and overshoot.

## Auxiliary fuse inrush question

The PSU's quoted inrush peak does not give pulse energy. An idealized 20 A rectangular pulse lasting 1 ms has I²t = 0.4 A²s; at 5 ms it is 2 A²s. Those examples differ fivefold while sharing the same peak. Use measured worst-case waveforms and the fuse manufacturer's pulse-life guidance, not a peak-only comparison with the 1 A auxiliary fuse.

## Metering sizing

See `METERING_DESIGN.md` for the 0.5 mΩ shunt and voltage-divider example. Their implementation is not present on the current PCB. No stated power, energy, power-factor or load-classification accuracy has been validated in hardware.
