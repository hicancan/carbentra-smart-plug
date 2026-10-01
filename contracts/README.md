# Plug wire boundary notes (shared contract authority)

The sole schema and semantic authority is now `carbentra-campus-platform/packages/iot-contract`, including `schemas/wire/`, `python/carbentra_iot_contract/plug_wire.py` and canonical examples. No schema is vendored or independently maintained here. The hardware-specific `device-capabilities.json` documents physical interfaces and release limits, with an explicit shared descriptor reference.

Topic routing remains `carbentra/v1/{device_id}/{hello,time,telemetry,receipt,cmd,ack}`. The wire payload remains v2 with additive local-input/manual-hold fields. Real firmware JSON encoding is compiled through host drivers and checked against the shared package by the platform Edge integration suite.

## Identity, units and evidence

`(device_id, boot_epoch, sample_seq)` is the immutable telemetry key. `sample_seq` is a canonical decimal string in 1..18446744073709551615, never a JavaScript number. The same key with different content is a conflict, not an update. An authenticated server derives receipt time; client time never replaces it.

Power is W; forward/reverse accumulated known energy is Wh since this boot. Never sum cumulative Wh, never relabel it kWh, never compare across boot epochs. The platform computes qualified adjacent deltas and converts Wh→kWh once; gaps, reverse flow, coverage, missing data and meter topology remain explicit. Counters or inferred savings do not make an uncalibrated sample usable.

`monotonic_ms` is the snapshot capture time; `measurement_monotonic_ms` is its last measurement. Feedback and board temperature are distinct observations; board temperature is not room or contact temperature. Optical absence of pulses never proves safe voltage absence.

Authenticated sample time is an interval: `unix_lower_s <= unix_s <= unix_upper_s`, width at most 5 seconds. Every value comes from the same current authenticated MQTT challenge/monotonic anchor at capture. Unknown time has `time_quality: unknown` and all three unix values null. Buffered retransmission never re-times or mutates a snapshot. The platform can display receipt-time fallback, but must exclude uncertain time from calendar allocation, forecasts and accounting.

Periodic telemetry carries `fault_latched`; a newly latched fault immediately adds a sample even without any new command. Offline is derived by the platform from received time/freshness, independently from electrical output state.

## Command outcomes

`REQUESTED_AWAITING_FEEDBACK` and `ACCEPTED_NO_CHANGE` are nonterminal. Even no-change commands wait for a fresh qualified observation. One execution can await feedback at a time; a new command is rejected as `BUSY_AWAITING_FEEDBACK`. The local five-second observation deadline never extends because of retries or connectivity.

Terminal outcomes include `OBSERVED_VERIFIED`, `FAILED_FEEDBACK`, `FAILED_SUPERSEDED`, and `TIMED_OUT`. They contain the same command ID/sequence, boot epoch, requested/deadline/observed monotonic times and actual feedback fields. A qualified observation must be at least 100 ms after request and strictly before the deadline to verify. Fault or local OFF supersedes the request. Terminal snapshots are retried unchanged while held in RAM; reboot can lose them, so the platform retains its independent timeout/unknown deadline and never infers success.

A durable replay sequence is written before a relay request. Default firmware disables relay actuation and commissioning, independently of any platform UI or command transport. No remote command clears a latched local fault.

## Persistence and cold TLS bootstrap

On-flash namespaces are `cb_journal`, `cb_factory`, `cb_secure`, each statically asserted ≤15 bytes. No deployed unit migration is assumed. Invalid previous overlength names could not have been written by ESP-IDF. Incompatible calibration v2 is rejected without erasure or automatic revision guessing; deliberate re-issuance from a real, fully identified per-unit calibration record is required.

Calibration v3 stores all 24 bytes of the zero-padded full board revision, including A/B/C distinction; CRC is accidental-integrity protection only. No default gains or production calibration files are shipped. This development format accepts 1..1,000,000 calibrated pulses/kWh and requires both coefficient banks to contain data; out-of-scope calibration requires a reviewed format change rather than silently accepting an overflowing scale.

TLS CA, hostname and certificate date verification stay enabled. Before starting MQTT, the endpoint obtains a ≤2-second challenge response signed by an independently commissioned P-256 public key. The canonical signed bytes are `CARBENTRA_TIME_V1\n{nonce}\n{unix_s}\n`; the signature is DER ECDSA-SHA256 encoded as base64. `cb_secure/time_url` is an HTTP endpoint carrying only public challenge/time/signature data, and `time_pub` is the independently provisioned PEM public key. Trust does not come from HTTP. Redirects are refused. No unverified TLS, SNTP or saved stale timestamp bootstraps certificate validity.

the shared platform `edge/time_bootstrap.py` is optional and requires an operator-supplied private-key file plus an independently accurate host clock. It never creates keys. No signer key, device key or certificate is included. The bootstrap runs in its own task so malicious latency cannot block local protection; failed refresh eventually stops MQTT. Provisioning, key rotation/revocation, accurate server time and broker ACL are explicit deployment responsibilities.

## Layer ownership and remaining gates

Firmware owns local protection and observation. Edge owns strict wire ingestion, durable transport, bounded dispatch and retries. Platform owns asset ontology/registry, policies, forecasts, optimization, interval/energy/carbon ledgers, command lifecycle and presentation. Future physical transport requires independent backend and edge opt-ins plus matching operator-attested release records and per-device allowlists; all remain OFF for this digital validation, and firmware actuation remains independently disabled. Device wire data contains no fabricated campus/room/model binding.

A passing target build, host tests or virtual broker loop is digital evidence only. Actual MCU timing/radio/TLS interoperability, relay response, per-unit calibration, power-loss recovery, security hardening and all mains/thermal/insulation/EMC qualification remain independent HOLD gates.
