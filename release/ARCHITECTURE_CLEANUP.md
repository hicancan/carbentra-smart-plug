# Canonical ownership cleanup

Current device work preserves one implementation per responsibility:

- The C firmware core owns local safety. The unused Python policy clone was removed after its unique scenarios were retained in the now 42-case C suite and 10,000 fault-priority checks
- The edge owns wire validation, durable SQLite receipts/outbox/inbox, authenticated transport and explicit dispatch gates. Its duplicate forecasting, planning and accounting code/tests were removed after replacement coverage passed in the platform backend
- The platform owns asset/binding ontology, forecasts, policy/approval workflows, interval energy and monetary/carbon accounting. Local device safety remains independent and cannot be overridden by cloud policy
- Device payload schema v2, exact bounded command schema and full calibration v3 are canonical. There is no unverified historical namespace or calibration compatibility shim; no deployed-device migration is assumed, no NVS is erased

## Historical working-tree material

Seventy-nine files (71,972,187 bytes) in `visuals/revA_baseline` were removed after tracing current generators, references and all freeze pins. This directory was a duplicate historical snapshot, not a dependency of the current Rev B source/build pipeline. The current scene, PCB/CAD and source generators remain unchanged by that removal. Git, including pre-cleanup commit `763972e`, retains the historical assets. Seventeen current hardware evidence checks still pass afterward.

Eighteen obsolete integrated electrical validation-history files were likewise removed after consumer tracing; the generator and documentation now use Git history rather than writing new archive snapshots. Active Rev B controller/meter/feedback/thermal module sources and the shared S-expression parser remain because the current integrated-board rebuild reads them. Older source/geometry used by active pipelines is not blindly deleted.

## Safety and verification boundary

The new physical command transport branch is complete code behind independent default-OFF platform and edge gates, matching operator release records and per-device allowlists. No actual physical deployment configuration was enabled. Positive branch tests use inert callbacks; broker tests use explicitly VIRTUAL/SIMULATED endpoints. Firmware actuation remains compiled OFF. None of this qualifies fabrication, calibration, energization or mains safety.

Current digital evidence is in `digital_checks_rev_b.json`, `firmware/validation.json` and the recertification report. Historical PASS records are never substituted for current source hashes or rerun checks.
