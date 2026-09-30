# Fixed-placement LV copper completion

The deliverable is `../candidate_lv.kicad_pcb`, with matching project and rule files.
The final actual KiCad report is `../validation/candidate_lv_drc.rpt`:

- 0 design-rule violations
- 0 low-voltage unconnected items
- 9 intentionally open mains-domain connections, including the two normally-closed relay contacts on `L_NC_UNUSED`
- 0 footprint errors reported

All 37 footprint placements and pad geometries are unchanged (33 electrical components and 4 mounting holes). Only the two K1 pad 12 net assignments were changed, as specifically requested. The 8 mm mains-to-LV rule explicitly includes `L_NC_UNUSED`; ground outlines have a corresponding notch, and the long EN track was locally offset 0.15 mm. U3's tiny ground island needed small local TEMP_ALERT and BUTTON route adjustments and an escape to a ground via. No DRC exclusions were added.

## Repeatable rebuild from fixed placement

The authoritative routing source is `completed_lv_recipe.json`, replayed by `rebuild_completed_lv.py`. The replay checks every footprint/pad position and pad dimension before replacing copper. It maps copper by net name rather than relying on net-code numbering. It refuses changed geometry, adds the requested NC net if needed, refills the ground planes, and writes matching clearance rules.

From the electronics directory:

    /usr/bin/python3 scripts/rebuild_completed_lv.py INPUT.kicad_pcb OUTPUT.kicad_pcb
    kicad-cli pcb drc OUTPUT.kicad_pcb -o validation/rebuilt_lv_drc.rpt --format report

Tested replay:

    /usr/bin/python3 scripts/rebuild_completed_lv.py candidate_lv.kicad_pcb /tmp/candidate_lv_rebuilt.kicad_pcb
    kicad-cli pcb drc /tmp/candidate_lv_rebuilt.kicad_pcb -o /tmp/candidate_lv_rebuilt_drc.rpt --format report

The replayed file also reports 0 violations and the same 9 mains-domain unconnected items. Do not apply the recipe after moving components without rerouting and review.

## Development provenance

`complete_lv.py` performs targeted A* routing between the previous report's disconnected LV items. `complete_lv_stitch.py` stitches eligible front-ground polygons to the rear plane. `complete_lv_nc.py` classifies the NC contacts as hazardous. `complete_lv_local.py` and `complete_lv_escape.py` implement the final local changes. These development helpers assumed the specific pre-completion board; use the recipe replay for routine rebuilding, rather than rerunning the development sequence on the finished board.

This is a developmental layout result. DRC connectivity and copper clearance do not validate mains safety, EMC, thermal behavior, load current capability, or production readiness. Main power paths remain intentionally unrouted.
