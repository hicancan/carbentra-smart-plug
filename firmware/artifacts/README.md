# Development-only target artifacts

Current ESP32-C3 binaries are produced by official ESP-IDF 5.4.3 from the source snapshot bound in `../validation.json`. All supplied application images are compiled with actuation disabled. `../target_build.log` and the source/artifact hashes bind the actual build; no earlier binary is substituted.

These files are digital build evidence. Do not flash or energize a unit on the strength of a passing build. Independent hardware release, measured per-unit calibration, owner credentials/ACL and signed-time provisioning remain required. No key or production calibration is included.
