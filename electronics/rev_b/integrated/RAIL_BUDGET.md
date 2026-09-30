# Integrated isolated-power review

**Result:** a conservative simultaneous design reservation is **3.89 W on the isolated 5 V output**. IRM-05-5 has useful margin at module ambient≤50 °C but its 3.75 W limit at 60 °C does not cover this reservation. The integrated candidate now selects the same-size/pin-compatible **IRM-10-5**, approved after the official pin-layout comparison. This review is neither measured temperature evidence nor a guaranteed maximum-current proof across all parts, firmware and transients.

## Reservation and evidence

| Branch | Basis | 5 V output power charged |
|---|---|---:|
| ESP32 + all isolated 3.3 V logic |550 mA at a conservative planning 3.4 V, divided by assumed 80% buck efficiency |2.3375 W|
| R05CT05S hot-island converter |200 mA datasheet input-current maximum at 5.125 V |1.025 W|
| Relay coil |100 mA design reservation at 5.125 V |0.5125 W|
| Other 5 V bias |2 mA design reservation |0.01025 W|
| **Total** |Approximately 0.797 A equivalent at 4.875 V |**3.88525 W**|

The ESP32-C3 module specifies an external supply capable of at least 0.5 A. Its published 25 °C TX peak is 345 mA in one radio mode; that number is not an all-PVT module-current ceiling. The 500 mA reservation is supply capacity, not a claim that the module continuously consumes it. Another 50 mA covers the isolator, feedback optocoupler, indicator/pullups, temperature sensors, thermal latch and substantial small-load margin. [Espressif module](https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf), [power-supply guidance](https://docs.espressif.com/projects/esp-hardware-design-guidelines/en/latest/esp32c3/schematic-checklist.html)

AP63203’s CCM feedback specification is 3.27–3.33 V. The 3.4 V planning value adds room beyond that table for this budget. Its 2 A rating exceeds the 550 mA reservation, but **80% efficiency is our design assumption, not a manufacturer-guaranteed floor** at 5 V input. Efficiency, inductance/saturation, DC-bias-reduced ceramic capacitance, layout and temperature must be checked on the actual build. Do not convert its 2 A nominal capability into a 2 A available system rail. [Diodes AP63203](https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf)

The selected TE relay has 5 V nominal coil and 0.403 W nominal coil power; TE’s product page lists 63 Ω.100 mA is a warm/room-temperature engineering allocation rather than a manufacturer worst-case. Coil-resistance tolerance, cold-soak copper resistance, pickup margin at the lowest supply, and the AO3401A/low-side-driver drop need checking. A120 mA sensitivity case adds 0.1025 W, bringing the total to 3.988 W. [TE RT314005](https://www.te.com/en/product-1-1649328-0.html)

## Hot-side island and no double counting

R05CT’s **200 mA input** allocation already includes the hot-side AFE, oscillator, isolator and converter loss. Do not add their output power again to the 5 V total. Selected 3.3 V mode has 80 mA typical quiescent input, so ideal-output-power/5 V is an unsafe budget shortcut. At 4.5 V input the 3.3 V output table allows 110 mA; at≥5 V it allows 150 mA. The rail minimum 4.875 V plus listed 200 mVp-p supply ripple remains above 4.5 V in a simple steady-state check, but startup/load-transient excursions are unverified. [RECOM RxxCTxx](https://recom-power.com/pdf/Econoline/RxxCTxx.pdf)

Hot-side reservation: ATM90E26 **15 mA allocated** versus 5.8 mA nominal datasheet total; ASV oscillator **10 mA maximum** in the 8.192 MHz frequency band; ISO6741 side 2 **12.1 mA maximum** at 50 Mbps/15 pF;2 mA pullup/other allocation. Total **39.1 mA**, about 0.137 W at 3.5 V. This is below the low-input 110 mA table limit and the referenced RECOM thermal curve around 60 °C; the latter was measured on a 54×85.6 mm,2-layer,105µm-copper board, not this integrated stack. ATM90E26’s supply current is typical-only, so 15 mA is an explicit allocation, not a sourced guaranteed maximum. [AFE](https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/Atmel-46002-SE-M90E26-Datasheet.pdf), [ASV](https://abracon.com/Oscillators/ASV.pdf), [ISO6741](https://www.ti.com/lit/ds/symlink/iso6741.pdf)

## Module-temperature margin

At the 198–242 VAC proposed operating input, the manufacturer input-voltage curve does not require the low-line derating used below 100 VAC. Local **module ambient**, not room temperature, controls the following horizontally mounted/free-convection curve readings:

| Module ambient | IRM-05 available | Margin vs 3.885 W | IRM-10 available | Margin vs 3.885 W |
|---|---:|---:|---:|---:|
|50 °C|5 W|+1.115 W|10 W|+6.115 W|
|60 °C|3.75 W|−0.135 W|7.5 W|+3.615 W|
|70 °C|2.5 W|−1.385 W|5 W|+1.115 W|
|80 °C|1 W|−2.885 W|2.3 W|−1.585 W|
|85 °C|0.25 W|−3.635 W|1 W|−2.885 W|

The IRM-05 cannot be advertised as a 5 W supply through 85 °C. The IRM-10 improves 60 °C headroom substantially but still cannot support this reservation at 80 °C. Curves are graph readings, not measured assembly results. [IRM-05](https://www.meanwell.com/Upload/PDF/IRM-05/IRM-05-SPEC.PDF), [IRM-10](https://www.meanwell.com/Upload/PDF/IRM-10/IRM-10-SPEC.PDF)

## Selected geometry-neutral upgrade

Both manufacturers’ current drawings identify case 222A:45.7×25.4×21.5 mm,38.5 mm across pin columns,10.75 mm input pair spacing and 8 mm output pair spacing,1.0 mm pins,3.5±1 mm projection. Pin functions match the existing symbol/footprint:1N,2L,3−V,4+V. IRM-10-5 gives 5 V/2 A,±2.5% output tolerance and 200 mVp-p ripple. Its 230 VAC cold-start inrush is 40 A typical, like IRM-05. Typical full-load efficiency is 77% rather than 71%; neither value proves the efficiency or case temperature at this design’s partial load. Actual input-fuse survival/I²t coordination still requires startup testing and manufacturer limits.

## Required bench closure

- Measure 5 V and 3.3 V under worst radio transmit, flash activity, relay pickup/release and sustained SPI; check brownout and thermal-trip behavior
- Measure supply/relay/collector/shunt/fuse temperatures at the actual maximum load and enclosure air temperature; distinguish actual air temperature from module case temperature
- Test undervoltage, repeated mains interruption, hot restart and the thermal latch’s power-ramp/held-reset cases
- Confirm the chosen coil allocation over allowed cold and hot conditions, and validate the 80% buck-efficiency assumption or replace it with measured bounds
- Revisit source interruption/fuse coordination after any module or protection substitution; larger power capability changes available fault energy

The numeric reproduction is `scripts/calculate_rail_budget.py`; the machine-readable result is `validation/rail_budget.json`.
