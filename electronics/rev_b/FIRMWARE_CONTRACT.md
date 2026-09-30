# Rev B metering firmware contract

Engineering contract; no flashed-hardware or calibrated accuracy claim.

## Electrical interface

JISO: 1 ISO_3V3, 2 ISO_GND, 3 SCLK (GPIO4), 4 MOSI (GPIO6), 5 MISO (GPIO5), 6 CS (GPIO7), 7 ISO_5V, 8 ISO_GND. ISO6741DWR separates every SPI signal; R05CT05S supplies the line-referenced 3.3 V domain. No direct hot-domain debugger.

Use 100 kHz, MSB first, SPI mode 3; validate timing on isolated-side logic analyzer only. Never infer link integrity from plausible numeric readings alone. No fabricated calibration coefficients are allowed.

## Verified ATM90E26 facts

Source: [Microchip datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/Atmel-46002-SE-M90E26-Datasheet.pdf), sections 4, 5, 6.2.

- 24 clocks per transaction: address byte (read bit7=1), then 16-bit data; CS remains low
- Maximum SPI rate 160 kbit/s; LastData 0x06 checks prior transfer
- SoftReset 0x00 accepts 0x789A
- SysStatus 0x01 is read/clear; calibration errors invalidate measurements
- Irms 0x48: unsigned, 0.001 A/count
- Urms 0x49: unsigned, 0.01 V/count
- Pmean 0x4A and Qmean 0x4B: signed two's complement, 1 W/var per count
- Frequency 0x4C: 0.01 Hz/count
- PowerF 0x4D: sign-magnitude, 0.001/count; 0x83E8 = -1
- Smean 0x4F: positive, 1 VA/count
- CS1 0x2C covers register bytes 0x21–0x2B; CS2 0x3B covers 0x31–0x3A. Low checksum byte is byte-sum modulo256; high byte is byte-XOR
- Energy registers 0x40–0x45 clear on read: never blindly retry an uncertain energy read

## Engineering integration requirements

The scales above apply after valid calibration. Store a versioned per-unit record with board revision, shunt/divider nominal values, measured reference conditions, gain/phase/offset coefficients, checksums, record CRC and traceable calibration identity. Reject wrong-revision or corrupt records. Startup without a valid record remains monitor-only/uncommissioned; driver availability does not authorize mains actuation.

Calibration needs voltage/current RMS gain, unity-PF active-power gain, inductive phase correction and low-current offset characterization, followed by multi-point validation. Use matched 100 R/330 nF shunt filters; their attenuation and actual input impedance must be included in calibration. Gain24 with 1 mΩ shunt yields 16 mV RMS at 16 A; inrush may saturate. The meter is neither a short-circuit interrupter nor a high-speed waveform classifier.

Read energy once per scheduled acquisition. If transfer outcome is uncertain, mark the accounting interval uncertain rather than double count or invent its energy. Avoid recursive LastData checks: verify the requested register once using LastData, then resume normal operations. A disconnected hot supply defaults isolator outputs high; 0xFFFF must not be accepted as valid telemetry.

Output feedback is a separate active-low pulse signal on GPIO3 via ACPL-K376 (3-pin:3V3/GND/OUTPUT_PRESENT_N). Rev B repurposes previous TMP102 ALERT GPIO3; temperature is polled over I2C. Independent thermal interruption still requires the actual series cutoff; software polling is not its replacement. See feedback deliverable for exact timing and thresholds.

## Startup and checksum enforcement

Reset with 0x00=0x789A; allow 100 ms conservative engineering settling, then check 0x20 and 0x30 read 0x6886. A valid profile contains all words 0x21–0x2B and 0x31–0x3A, even unused-channel values, so checksum inputs are deterministic. Start each bank with 0x5678 before writing its words; this command resets that bank. Write CS1/CS2 last, then write both start registers to 0x8765. Check computed checksum readbacks and reject SysStatus bits15–12. Do not use factory defaults as calibration. For gain24 the MMode bits15–13 are011; preserve other intentionally configured fields. MMD1=0/MMD0=1 physically selects L-only metering.

Maintain at least 5 µs CS-high between transactions and 5 µs after last clock before deasserting CS. Profile meter constant must be explicit (pulses/kWh): energy_count/10/meter_constant gives kWh. An uncertain read-clear operation may be recovered by repeated LastData reads without rereading the target, as described in AN46102 §4.3; if consistency still fails, record an unknown interval. No hardcoded default energy constant is authorized.
