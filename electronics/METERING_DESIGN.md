# Metering extension — interface design, NOT fabricated hardware

**Status: critical open gate.** The main controller carries J3; the metering daughterboard is a pin-level candidate architecture only. There is no routed daughterboard, calibration evidence, energy-accuracy claim, or allocated enclosure volume for it. Until it exists and is validated, the socket cannot execute measurement-based load recognition or protection. Never substitute synthetic telemetry as hardware validation.

## Partition

The ADE9153A and its analogue conditioning are **mains referenced** (`GND_HOT`), even though their supply is only 3.3 V. `GND_HOT` must never join `GND_ISO`, protective earth, a debugger, USB or an exposed control. Candidate ADuM3151 separates the SPI domains. Its insulation ratings do not certify this assembly: working voltage, pollution degree, transient category, material group, altitude, package spacing and regulatory applicability require review. A separately qualified isolated power converter is also required; an ordinary common-ground 3.3 V supply defeats the signal barrier.

## Pin contract (mainboard J3)

| J3 | Main net | ADuM3151 controller side | ADuM3151 hot side → ADE9153A |
|---|---|---|---|
| 1 | +3V3_ISO | 1 VDD1 | No direct cross-barrier connection |
| 2 | GND_ISO | 2,10 GND1 | No direct cross-barrier connection |
| 3 | SPI_SCLK | 3 MCLK | 18 SCLK → 31 SCLK |
| 4 | SPI_MOSI | 4 MO | 17 SI → 29 MOSI |
| 5 | SPI_MISO | 5 MI | 16 SO ← 30 MISO |
| 6 | SPI_CS | 6 MSS | 15 SSS → 32 SS |

ADuM3151 hot supply: 20 VDD2 to +3V3_HOT; 11,19 to GND_HOT. Decouple both sides separately. Unused controller inputs 7/8 are held at valid logic; unused outputs 9/13/14 are not connected. Hot input 12 is tied to GND_HOT. Main J3 deliberately omits IRQ and reset: poll meter status; implement local hot-domain reset supervision for ADE pin 28. A later connector revision is required for isolated interrupt and host reset. Begin firmware integration at 1 MHz SPI, then verify timing rather than assuming maximum rates.

## Candidate analogue front end and sizing

A four-terminal **0.5 mΩ shunt** in the switched line path gives 8 mV rms and 0.128 W at 16 A; its sine-wave peak is 11.3 mV. Use Kelvin routing to IAP8/IAN7 through matched anti-alias filters. Pulse energy, temperature coefficient, solder fatigue, short-circuit coordination and overload power must be qualified. A catalog wattage alone is insufficient. Candidate family: Vishay WSK2512 (exact resistance, tolerance and pulse qualification not selected): https://www.vishay.com/en/resistors-fixed/current-sensing/ . A resistive shunt is not an isolating element.

Voltage channel candidate: a 996 kΩ high leg (four 249 kΩ resistors in series) and 1 kΩ lower leg. At 264 V rms this ideal divider produces 0.2648 V rms / 0.3745 V peak; high-leg dissipation is about 70 mW total. This is a sizing calculation, NOT an approved network. Working-voltage/pulse-rated resistors, surge coordination, anti-alias poles, creepage along the series chain and exact common-mode topology require review against ADE9153A's application circuit. Do not connect a simple divider to an arbitrary MCU ADC.

ADE9153A pin planning: current input7/8, voltage14/15, optional CT11/12; grounds1/9/17/20 remain hot; supplies5/24 use 3.3 V hot. Crystal interface3/4; 12.288 MHz reference architecture. Internal outputs2/10/16 and reference18 need their specified local capacitor networks and must not power other devices. mSure network6/13/19/21/22/23 is not fully designed here; standard calibration is the default development path. **Exposed pad must remain floating** per datasheet. No convenient ground thermal pad substitution.

## Production gates

1. Complete hot-domain schematic including power, surge, reset, crystal, reference, analogue filters and all unused-pin treatment
2. Allocate daughterboard envelope or redesign the main PCB; prove barrier clearances in 3D including wiring and fasteners
3. Validate isolation components for actual product standard and continuous working voltage
4. Calibrate against a traceable reference at multiple currents, power factors, temperatures and distorted waveforms; preserve per-unit coefficients with CRC/version
5. Characterize noise and failure detection: unplugged J3, invalid CRC/status, frozen readings, brownout and implausible RMS → reject new automatic commands / hold commissioned state; separately qualified hardware fault protection may interrupt the load
6. No automatic restart after a thermal/electrical fault without explicit, bounded policy and valid sensor recovery

## Primary references, checked 2026-09-30

- ADE9153A Rev0, pin table pp9–10 and application circuit: https://www.analog.com/media/en/technical-documentation/data-sheets/ade9153a.pdf
- ADuM3151/3152/3153 RevC, pin table p13 and insulation information: https://www.analog.com/media/en/technical-documentation/data-sheets/adum3151_3152_3153.pdf

This specification records engineering synthesis. It does not copy the complete manufacturer reference design and has not undergone electrical sign-off.
