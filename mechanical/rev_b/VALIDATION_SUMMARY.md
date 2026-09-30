# CARBENTRA CARBENTRA-P16-EVT-B · Final digital review snapshot

- Envelope:108 ×93 ×65 mm nominal; original design, single16A-class interface
- Mechanical geometry:71 physical parts and1 explicitly non-physical RF slack reservation
- Combined system:234 physical model objects(71 mechanical +144 PCB placement/body/lead +19 remote head); reservation retained only as reference in native CAD
- BRep fit:all valid single solids; zero unintended mechanical, main-board/lead or remote-head intersections. Conductive joints, clip engagement and nominal thread-major/pilot overlaps are listed separately
- Conductive joint geometry:all modeled external interfaces connect; PE forms one continuous solid
- Receptacle spring candidate:0.4 mm leaves,1.7 mm free gap;1.8/1.95 mm prescribed inserted states pass with0.05/0.125 mm displacement per leaf and no rigid insertion obstruction
- Shutter:11 tested states; independent single-pawl attempts are mechanically blocked, both-released travel and full-open passages are clear
- Main-board segregation:8.516645 mm minimum nominal exposed-primary to isolated copper, including the filled plane; passes the project8.4 mm geometry screen
- RF slack:remaining44.134 mm of the100 mm coax allocated in a retained service-loop reservation, assumed minimum bend radius6 mm; default-hidden and excluded from physical STEP/mass/procurement
- Export check:source and delivered cleaned BRep geometry match within1e−10 numeric serialization tolerance; STEP roundtrip has234 valid solids, relative summed-volume difference2.12e-08

## Scope and remaining release gates
This freezes the bounded digital review configuration. It is not a fabrication, energization or certification release. Nominal3D separation is not a qualified clearance/creepage result. The remote thermal pickup intentionally relies on0.5 mm solid insulation, whose material, compression, edges and dielectric behavior require qualification. Contact force/fatigue, plug/receptacle gauges, blade sleeves, fuse/thermal coordination, conductor terminations, screw torque/retention, RF connector/slack strain relief, thermal rise, wall-socket loading and EMC remain explicit gates in docs/.

The PCB bodies and several connector/lead geometries are nominal/max envelopes, not complete vendor internal CAD. The RF reservation allocates routing space; it does not pretend to be a purchased component or an exact cable centerline. Exterior/main-current packaging stayed fixed during the final checks.
