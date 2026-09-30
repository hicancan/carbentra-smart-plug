# Protection and RF candidate integration

Status: real component candidates and nominal geometry selected; application qualification and production sign-off remain open. See the mechanical assembly for allocated pockets and wire-routing envelopes. These parts are external to the main PCB and must be included in the final electrical design, harness drawings and certification bill of materials.

| Ref | Candidate | Geometry / preliminary purpose | Primary source |
|---|---|---|---|
| FH1 | SCHURTER OGN 0031.8201 | THT 22.5 mm pitch; nominal body 25 × 9.6 × 11.5 mm; 4 mm leads. Open holder inside inaccessible enclosure. Do not add a cover without recalculating derating | https://www.schurter.com/en/datasheet/typ_ogn.pdf |
| F_MAIN | Littelfuse 0216016.MXP | 5 × 20 mm ceramic, 16 A fast-acting, 250 VAC candidate. Application current and fault coordination unqualified | https://www.littelfuse.com/assetdocs/littelfuse_fuse_216_datasheet.pdf?assetguid=69cb9c39-1497-4ecc-b09a-c0168520688e |
| TF1 | Sensience MICROTEMP G5, 110°C candidate | Body 14.7 × Ø4 mm; nominal Ø1 mm leads. G5A01110C ordering suffix requires procurement confirmation; G5 family chosen over 10 A G4. Temperature selection remains provisional | https://www.sensience.com/wp-content/uploads/2022/12/Microtemp_Catalog.pdf |
| F_AUX | Littelfuse 0215001.MXEP | 1 A time-lag 250 VAC, axial ceramic body 21.5 ±1 × Ø5.5 ±0.3 mm; Ø0.65 mm leads, 40 ±1 mm each before forming. Minimum lead bend distance and mounting stand-off per datasheet | https://www.littelfuse.com/~/media/electronics/datasheets/fuses/littelfuse_fuse_215_datasheet.pdf.pdf |
| ANT1 | Taoglas FXP73.07.0100A | Flexible 47 × 7 × 0.1 mm 2.4 GHz antenna, 100 mm 1.13 mm coax, MHF I / U.FL-compatible connector, 2.5 dBi candidate | https://www.taoglas.com/datasheets/FXP73.07.0100A.pdf |

## Electrical order

L blade → F_MAIN → TF1 → protected line junction.

The junction splits into J1.1 (L_FUSED, relay common input) and F_AUX → J5.1 (L_AUX_FUSED, isolated supply input). N blade connects J1.2, J5.2 and J2.2; switched output is K1 NO → J2.1 → socket L contact. PE remains a separate uninterrupted protective path. This description does not validate physical routing, conductor sizes, splices, terminations, fuse supports or any particular fault duty.

The G5 interruption ratings are resistive. A relay weld should leave TF1 capable of interrupting the independently detected contact over-temperature condition, but only if physical coupling, current category, fault current and interruption tests establish that function. Merely mounting TF1 nearby does not establish protection.

## Exact missing data to release protection

- Target outlet standard/jurisdiction, branch circuit type and prospective short-circuit current at the outlet, including upstream protective device time-current and let-through curves
- Maximum continuous current, ambient temperature, local fuse-pocket temperature and orientation; holder derating and fuse self-heating under enclosure conditions
- Load inrush waveform and repetition: peak, pulse width, I²t and locked-rotor / capacitive behavior. The fast 16 A fuse is a first resistive-load candidate, not an approved compressor profile
- PSU input inrush duration/I²t and worst-case cold/hot restart tolerance. A listed 20 A peak alone cannot prove a 1 A time-lag fuse will survive
- Socket contact and plastic allowable temperatures, sensor-to-contact thermal gradient, heat-transfer delay and abnormal-condition overshoot. A provisional 110°C cutoff is not an approved user-accessible or plastic temperature limit
- TF1 insulated attachment method, sleeve properties, lead forming/crimp tooling and solder heat controls; exact suffix and approvals for the final market
- Fuse-interruption approval differences: main 216 series ratings depend on amperage and agency; determine the applicable certificate rather than extrapolating a family headline

## RF gate

ANT1 is connected to U1's existing external RF socket. No PCB RF trace or additional U.FL footprint is required. Mechanical placement along the inside upper wall is a candidate; antenna tape bonding, coax bend radius, strain relief and retention need production review. The coax endpoint is currently an approximate module-envelope coordinate, not vendor-verified connector-axis geometry.

Check Espressif's permitted antenna type/gain and modular approval integration conditions for the selected market. A Taoglas antenna certificate does not certify this end product. Enclosure/contact metal, protective conductors, human proximity and wiring can detune the antenna; measure return loss and radiated performance in the assembled unit. This design contains no infrared emitter or air-conditioner protocol transmitter.
