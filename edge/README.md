# Shared Edge runtime

There is no second Plug-only Edge implementation in this repository. The sole runtime is `carbentra-campus-platform/edge`; schemas, semantic validators and canonical examples live in that repository's `packages/iot-contract`.

Set `CARBENTRA_PLATFORM_ROOT` to the actual local platform checkout. No remote repository or deployment URL is guessed. Create its project environment with `uv venv --python 3.12`, install its root `uv.lock` with `uv sync --locked`, then run its `edge/service.py` with the reviewed per-device enrollment/configuration. See the platform Edge README/runbook for MQTT mTLS, HMAC-authenticated Sense GATT, channel control, offline outbox and deployment gates.

For cross-repository verification, set `CARBENTRA_PLATFORM_ROOT` and run `pwsh -NoProfile -File scripts/check_windows.ps1 -BuildTarget` from this hardware checkout. It compiles the actual MSVC/mbedTLS firmware gates and uses the shared platform environment. Tool paths and CAD/GPU checks are documented in [Windows development](../docs/WINDOWS_DEVELOPMENT.md). Missing shared source or dependencies is an error. Named POSIX permission checks execute in the complementary Linux suite; Windows executes all three real firmware integration gates. Evidence records both summaries instead of treating platform-specific exclusions as passes.

Independent hardware CI runs only its own C host regression, PCB evidence and ESP32-C3 compilation. Cross-repository cryptography/wire/MQTT proof belongs to the shared platform integration job/workspace. `PROVENANCE.json` records the retired source snapshot; Git history retains the former code. Historical broker evidence is not asserted against new sources. No physical dispatch gate is enabled by migration.
