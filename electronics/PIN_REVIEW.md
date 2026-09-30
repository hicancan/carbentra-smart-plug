# Pin and footprint review record

Digital connectivity check: `validation/net_pin_consistency.json` compares every assigned schematic pin in a KiCad-exported netlist to the PCB pad net. This catches pin-number drift, but it does not certify the circuit.

| Component | Checked implementation | Basis and remaining review |
|---|---|---|
| U1 | ESP32-C3-WROOM-02U; 1=3V3, 2=EN, 9/19=GND; IO4/5/6/7 = SPI; IO10 = relay; IO18/19 = button/LED; IO0/1 = I²C | Installed KiCad symbol/footprint; Espressif module datasheet. Pins 13/14 are therefore unavailable for native USB. External RF connector-axis model still approximate |
| U2 | AP63203WU; 1=FB, 2=EN, 3=IN, 4=GND, 5=SW, 6=BST; TSOT-23-6 | Diodes AP63200-family datasheet and KiCad symbol. Corrected pin map checked in exported netlist. Inductor/capacitor DC bias and switching-loop layout need review |
| Q1 | AO3400A; 1=G, 2=S, 3=D; SOT-23 | AOS official AO3400A datasheet. Guaranteed low-gate drive selection replaces the earlier 2N7002 development candidate |
| D1 | SS14 cathode pad 1 → +5V_ISO; anode pad 2 → COIL_LOW | KiCad SMA footprint and diode symbol. Verify exact vendor marking and coil suppression/release timing |
| K1 | TE RT314005; A1/A2 coil; 11 common; 14 NO; 12 unconnected externally but hazardous L_NC_UNUSED; duplicated high-current pads retain common pin numbers | TE RT1 candidate and KiCad 16 A Form C footprint. Exact production suffix and contact-load category remain approval gates |
| PS1 | Mean Well IRM-03-5; 1=L, 3=N, 14=−V, 16=+V; pad 5 unused | Mean Well IRM-03 datasheet mechanical drawing and native KiCad THT footprint |
| U3 | TMP102AIDRLR; 1=SCL, 2=GND, 3=ALERT, 4=ADD0→GND, 5=V+, 6=SDA | TI TMP102 datasheet and SOT-563. This measures PCB temperature, not a guaranteed socket-contact hot spot |
| J1/J2/J5 | Phoenix MKDS 3/2-5.08 part 1711725; 5.08 mm pitch, 1.3 mm holes; installed height 18 mm | Phoenix current product PDF and matching KiCad MKDS-3 footprint. Current rating depends on wire, temperature and approval category |
| SW1 | OMRON B3F-1000 candidate; duplicate pads 1 form one side, duplicate pads 2 form other; 6 × 6 mm body | Library SW_PUSH_6mm footprint; exact actuator height and manufacturer lead tolerance require independent review |
| LED1 | Kingbright WP710A10GD candidate; 1 cathode, 2 anode; D3.0 mm footprint | Candidate part family; exact optical/mechanical drawing still procurement-review gate |

## Primary sources

- https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf
- https://www.diodes.com/datasheet/download/AP63200-AP63201-AP63203-AP63205.pdf
- https://www.aosmd.com/res/data_sheets/AO3400A.pdf
- https://www.meanwell.com/Upload/PDF/IRM-03/IRM-03-SPEC.PDF
- https://www.te.com/en/product-1-1649328-0.html
- https://www.ti.com/lit/ds/symlink/tmp102.pdf
- https://www.phoenixcontact.com/en-gb/products/printed-circuit-board-terminal-mkds-3-2-508-1711725?type=pdf

No board-level current, EMC, isolation, metering or protection test has been performed.
