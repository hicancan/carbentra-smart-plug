# CARBENTRA CARBENTRA-P16-EVT-B · Insulation-domain proximity audit

**Engineering development only. No electrical insulation or energization approval.**

- Primary source regions: 53
- Source files changed during this audit: 0
- Native filled-zone partitions: 54
- Positive-volume intersections against all target groups: 0 (package/guide overlaps are not automatically electrical shorts)
- Main PCB bottom z11.5; actual native pad/track net names classify domains
- All tabulated distances are nominal Euclidean BRep separation, not qualified clearance or creepage

## Key engineering findings

| Region class | Source | Target | Nominal distance mm |
|---|---|---|---:|
| exposed_primary_to_any_isolated_copper | Blade_L | Track_In2.Cu_2159 [SPI_CS] | 8.5166 |
| exposed_primary_to_isolated_external_copper | Blade_L | Track_B.Cu_447 [+5V_ISO] | 8.7949 |
| bare_link_ends_to_isolated_external_copper | PowerCore_L_RAW__bare_start | Pad_F.Cu_U301_5_4_0 [GND_ISO] | 9.2175 |
| primary_solder_tails_to_isolated_external_copper | MainB_R304_Tail2 [HOT_FB_N_MID] | Pad_F.Cu_PS101_3_2_0 [GND_ISO] | 8.9965 |
| covered_link_core_to_isolated_external_copper | PowerCore_L_RAW__covered | Track_B.Cu_443 [+5V_ISO] | 9.9018 |
| exposed_primary_to_controls | PowerCore_L_PROTECTED__bare_start | LocalButton_GuideOuterEnvelope | 14.6049 |
| exposed_primary_to_case_screw_metal | MainB_F501_FormedLead__1 [HOT_GND] | Screw_0 | 9.5373 |
| exposed_primary_to_RF_routing_reservation | PowerCore_L_FUSE_THERMAL__bare_end | RFServiceSlackEnvelope | 20.2033 |
| covered_link_core_to_RF_routing_reservation | PowerCore_L_FUSE_THERMAL__covered | RFServiceSlackEnvelope | 8.6253 |
| covered_link_core_to_case_screw_metal | PowerCore_L_PROTECTED__covered | Screw_0 | 8.7167 |
| covered_link_core_to_controls | PowerCore_L_PROTECTED__covered | LocalButton_GuideOuterEnvelope | 8.9391 |

The exposed-primary minimum nominally meets the project 8.4 mm geometric screen. This is not a standard-derived acceptance criterion or a tolerance/insulation pass. Internal-layer distances include solid insulation. The thermal coupling is a separate 0.5 mm nominal solid-insulation interface.

Metal-to-metal positive-volume crossings in the checked pairs: 0. No-crossing does not establish safe insulation.

## Smallest pairs by target group

### isolated_external_copper

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| Blade_L | Track_B.Cu_447 [+5V_ISO] | 8.7949 | 0 |
| MainB_R304_Tail2 [HOT_FB_N_MID] | Pad_F.Cu_PS101_3_2_0 [GND_ISO] | 8.9965 | 0 |
| MainB_K101_Tail013 [HOT_NC] | Pad_F.Cu_U301_5_4_0 [GND_ISO] | 9.0540 | 0 |
| PowerCore_L_RAW__bare_start | Pad_F.Cu_U301_5_4_0 [GND_ISO] | 9.2175 | 0 |
| MainB_K101_Tail12 [HOT_NC] | Pad_F.Cu_U202_8_7_0 [GND_ISO] | 9.4613 | 0 |
| PowerCore_L_RAW__covered | Track_B.Cu_443 [+5V_ISO] | 9.9018 | 0 |

### isolated_solder_tails

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| Blade_L | MainB_K101_TailA1 [COIL_5V] | 9.2306 | 0 |
| MainB_R304_Tail2 [HOT_FB_N_MID] | MainB_PS101_Tail3 [GND_ISO] | 9.9947 | 0 |
| PowerCore_L_RAW__bare_start | MainB_K101_TailA1 [COIL_5V] | 10.1260 | 0 |
| PowerCore_L_RAW__covered | MainB_K101_TailA1 [COIL_5V] | 10.5018 | 0 |
| MainB_R303_Tail2 [HOT_FB_AC2] | MainB_PS101_Tail3 [GND_ISO] | 11.4134 | 0 |
| MainB_K101_Tail12 [HOT_NC] | MainB_K101_TailA2 [COIL_LOW] | 14.1600 | 0 |

### isolated_package_envelopes

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| Blade_L | MainB_R305 | 9.1138 | 0 |
| PowerCore_L_RAW__bare_start | MainB_R305 | 9.7418 | 0 |
| MainB_K101_Tail013 [HOT_NC] | MainB_R305 | 10.8809 | 0 |
| PowerCore_L_RAW__covered | MainB_R305 | 11.2196 | 0 |
| MainB_R303_Tail2 [HOT_FB_AC2] | MainB_C107 | 13.0559 | 0 |
| MainB_K101_Tail12 [HOT_NC] | MainB_CI201 | 13.3909 | 0 |

### accessible_controls_and_guide_envelopes

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| PowerCore_L_PROTECTED__covered | LocalButton_GuideOuterEnvelope | 8.9391 | 0 |
| PowerCore_L_PROTECTED__bare_start | LocalButton_GuideOuterEnvelope | 14.6049 | 0 |
| ThermalLead1 | LocalButton_GuideOuterEnvelope | 15.7205 | 0 |
| ThermalBody | LocalButton_GuideOuterEnvelope | 18.8751 | 0 |
| Contact_L | LocalButton_GuideOuterEnvelope | 18.9823 | 0 |
| PowerCore_L_OUTPUT__bare_end | LocalButton_GuideOuterEnvelope | 20.9823 | 0 |

### accessible_case_screws

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| PowerCore_L_PROTECTED__covered | Screw_0 | 8.7167 | 0 |
| MainB_F501_FormedLead__1 [HOT_GND] | Screw_0 | 9.5373 | 0 |
| MainB_PS101_Tail1 [HOT_N] | Screw_1 | 9.9434 | 0 |
| PowerCore_L_FUSE_THERMAL__covered | Screw_1 | 12.4602 | 0 |
| PowerCore_L_RAW__covered | Screw_0 | 14.4303 | 0 |
| PowerCore_L_FUSE_THERMAL__bare_start | Screw_1 | 14.8114 | 0 |

### rf_service_loop_reservation

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| PowerCore_L_FUSE_THERMAL__covered | RFServiceSlackEnvelope | 8.6253 | 0 |
| PowerCore_L_FUSE_THERMAL__bare_end | RFServiceSlackEnvelope | 20.2033 | 0 |
| ThermalLead2 | RFServiceSlackEnvelope | 21.2863 | 0 |
| ThermalBody | RFServiceSlackEnvelope | 25.5945 | 0 |
| Contact_L | RFServiceSlackEnvelope | 27.2576 | 0 |
| Contact_N | RFServiceSlackEnvelope | 39.1581 | 0 |

### isolated_internal_copper

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| Blade_L | Track_In2.Cu_2159 [SPI_CS] | 8.5166 | 0 |
| MainB_R304_Tail2 [HOT_FB_N_MID] | Pad_In1.Cu_PS101_3_2_0 [GND_ISO] | 8.9965 | 0 |
| PowerCore_L_RAW__bare_start | Track_In2.Cu_2159 [SPI_CS] | 9.0283 | 0 |
| PowerCore_L_RAW__covered | Track_In2.Cu_2159 [SPI_CS] | 9.3294 | 0 |
| MainB_R303_Tail2 [HOT_FB_AC2] | Track_In1.Cu_1063 [GND_ISO] | 10.2067 | 0 |
| MainB_K101_Tail12 [HOT_NC] | FilledZone_In2.Cu_4_cell_60_60_0 [GND_ISO] | 10.4454 | 0 |

### mixed_domain_package_envelopes

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| MainB_PS101_Tail1 [HOT_N] | MainB_PS101 | 0.0000 | 0 |
| MainB_PS101_Tail2 [HOT_AUX_FUSED] | MainB_PS101 | 0.0000 | 0 |
| MainB_K101_Tail11 [HOT_LOAD] | MainB_K101 | 0.0000 | 0 |
| MainB_K101_Tail012 [HOT_LOAD] | MainB_K101 | 0.0000 | 0 |
| MainB_K101_Tail12 [HOT_NC] | MainB_K101 | 0.0000 | 0 |
| MainB_K101_Tail013 [HOT_NC] | MainB_K101 | 0.0000 | 0 |

### remote_sensor_assembly

| Primary region | Target | Distance mm | Overlap mm³ |
|---|---|---:|---:|
| Contact_L | RemoteHead_assembled_all_solids | 0.5000 | 0 |
| ThermalBody | RemoteHead_assembled_all_solids | 5.5350 | 0 |
| ThermalLead1 | RemoteHead_assembled_all_solids | 7.1366 | 0 |
| ThermalLead2 | RemoteHead_assembled_all_solids | 7.1366 | 0 |
| Contact_N | RemoteHead_assembled_all_solids | 8.4065 | 0 |
| PowerCore_L_FUSE_THERMAL__bare_end | RemoteHead_assembled_all_solids | 8.8717 | 0 |

## Thermal-pickup interface

| Member | Distance to world-placed isolated head, mm |
|---|---:|
| Contact_L | 0.5000 |
| ThermalPad | 0.0000 |
| ThermalBody | 5.5350 |
| ThermalLead1 | 7.1366 |
| ThermalLead2 | 7.1366 |

Nominal0.5mm thermal pad intentionally separates primary pickup and isolated head. Solid-insulation material/system qualification remains OPEN.

## Positive-volume intersections

No positive-volume intersections were found in these tested pairs. This does not prove electrical separation, safe access, or compliant solid insulation.

## Interpretation and open gates

- All distances are direct Euclidean geometry, not a solved free-air path or surface creepage path. Plastic may lie between nearest points.
- Six covered links have1mm nominal carrier wall,0.2mm nominal radial copper-to-carrier bore gap and unqualified resin/joints. Proximity through that plastic is not an8mm air-gap pass.
- Thermal pad0.5mm is an intentional primary/isolated solid-insulation interface, not certified insulation.
- Component envelopes use nominal/max vendor dimensions or F.Fab rectangles, not manufacturer detailed CAD. lead_reserve geometries are conservative pin reservations.
- Copper z/thickness are visualization inputs(.07outer/.035inner), not a released layer stack. Via columns are conservative annular envelopes.
- Internal tracks/pads and native filled GND_ISO plane polygons are included in internal-copper results. Filled polygons are partitioned using exact KiCad integer clipping. Internal-layer separation is solid insulation, not an air-clearance result. Native PCB DRC remains necessary.
- Accessible pusher and guide-envelope distances are to insulating geometry, not standardized access probes or touchable metal.
- RFServiceSlackEnvelope is non-physical reference geometry, excluded from physical part count/mass; distances to it are conservative routing-reservation distances, not actual coax-shield clearance. About44mm service-loop allocation assumesR>=6mm/loopR~7mm; vendor bend and strain relief remain unqualified.
- Four case screws are modeled metallic major/shaft/head envelopes; distance to an embedded shaft is not a certified touch path. Boss plastic and partial-withdrawal access require review.
- ThermalBody is conservatively treated as a potentially-primary metal/body envelope until its exact construction and insulation status are qualified; it is separate from the actual exposed TF1 lead solids.
- No tolerance, warpage, contamination, material CTI, impulse, working-voltage, dielectric, thermal, spring-force or fault-withstand qualification.
- Source CAD is opened read-only and not recomputed/saved; exposed-link segmentation is reconstructed from current power_links.py. Input hash consistency is reported.

## Evidence and repeatability

Run `/usr/bin/python3 mechanical/rev_b/insulation_domain_audit.py` from the repository. Full source hashes, exact closest-point coordinates, per-region minima and lead/pad assignments are in `insulation_domain_report.json`. No source geometry is modified.

Primary references: [GB1002-2024 official record](https://openstd.samr.gov.cn/bzgk/std/newGbInfo?hcno=F8C9E208891B7BB5AF1B3E64933693C2), [SHF fuse](https://www.schurter.com/en/datasheet/typ_SHF_6.3x32.pdf), [CQP clips](https://www.schurter.com/en/datasheet/typ_CQP.pdf). These sources do not certify the custom assembly.
