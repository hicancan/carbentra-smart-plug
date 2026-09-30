# CARBENTRA board and harness interfaces

All world coordinates below are millimetres. MainB uses x=PCB_x−50, y=42.5−PCB_y and board bottom z=11.5. Its top surface is z=13.1. HeadB exports already use world coordinates.

## Thermal head

The three rear-exit head pads map one-to-one to main connector J403:

| Net | Head J4 / integrated J404 pin | Head world XY | Main J403 pin / world XY |
|---|---|---|---|
| +3V3_HEAD / +3V3_ISO | 1 | (+13.8272413, −7.75) | 1 / (+44, +3.50) |
| GND_HEAD / GND_ISO | 2 | (+13.8272413, −5.21) | 2 / (+44, +0.96) |
| THERM_RETURN / TH_THERM_RETURN | 3 | (+13.8272413, −2.67) | 3 / (+44, −1.58) |

Head component-side pad copper is approximately z=41.83; the reserved rear pigtail exit plane is z=39.865. Main J403’s male-header envelope ends at z=21.48. These are modeled interfaces, not a qualified mated connector stack: the female contact/housing, positive retention, wire gauge, creepage along the harness and strain relief remain assembly selection/verification items. Do not route isolated sensor wires against exposed live metal; the thermal pad and retained carrier must supply the qualified insulating barrier.

## External RF connector

Espressif’s official v1.7 module drawing locates the ESP32-C3-WROOM-02U antenna connector axis 2.75 mm from the right module edge and 2.30 mm below its top edge. The standard footprint body begins at local (−9, −7.4), so the connector axis is local (+6.25, −5.10). For U101 at PCB (80, 23), this is PCB (86.25, 17.90), or **world (+36.25, +24.60)**.

The module substrate is 0.8 mm and the unmated connector drawing gives 1.25±0.15 mm height. Ignoring the unverified module solder stand-off, the connector rim is nominally z=15.15. This Z datum is a derived nominal, not a verified mated-plug/cable axis. Reserve the actual plug envelope, cable bend radius and strain relief separately. The total module height is 3.2±0.15 mm; the body export reserves 3.35 mm above MainB, ending at world z=16.45. The earlier 2.4 mm shield-only proxy omitted the module substrate and is superseded.

The selected antenna candidate remains Taoglas FXP73.07.0100A: external 47×7×0.1 mm film antenna with a 100 mm, 1.13 mm coax and compatible first-generation connector. Antenna placement, adhesive retention, detuning, radiated performance and final regulatory authorization remain unverified.

Sources: [Espressif module datasheet, figures 10-2 and 10-3](https://www.espressif.com/sites/default/files/documentation/esp32-c3-wroom-02_datasheet_en.pdf), [Taoglas FXP73.07.0100A](https://www.taoglas.com/datasheets/FXP73.07.0100A.pdf)

## Mains terminal and firmware interfaces

J201.1 is protected line/HOT_GND, J201.2 neutral/HOT_N. J102.1 is switched line/HOT_SWITCHED, J102.2 neutral/HOT_N. PE bypasses the board and every switching/protection contact. Terminal wire-entry direction is horizontal; top screws are not wire-entry ports. See `ELECTRICAL_SOURCE.md` and the mechanical endpoint manifest for side-entry and tolerance reservations.

The firmware mapping and verified meter register/scaling contract are in `../FIRMWARE_CONTRACT.md`. GPIO3 is post-switch AC-presence feedback; the polled TMP102 alert output is not tied to that GPIO. The independent thermal latch has no MCU rearm input.
