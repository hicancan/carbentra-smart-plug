#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../.."
export ASAN_OPTIONS=detect_leaks=0
EVIDENCE="${CARBENTRA_EVIDENCE_DIR:-$PWD}"
: "${CARBENTRA_PLATFORM_ROOT:?Set explicit shared platform checkout}"
: "${CARBENTRA_SWITCH_COMMAND_TEST_BINARY:?Set the externally compiled actual Switch C decoder gate for shared Edge release checks}"
test -x "$CARBENTRA_SWITCH_COMMAND_TEST_BINARY" || { echo 'Switch C decoder gate is not executable' >&2; exit 1; }
export CARBENTRA_SWITCH_COMMAND_TEST_BINARY
mkdir -p "$EVIDENCE/firmware/tests" "$EVIDENCE/firmware/evidence"
bash firmware/tests/run_host_tests.sh 2>&1 | tee "$EVIDENCE/firmware/tests/host_results.txt"
bash firmware/tests/run_crypto_tests.sh 2>&1 | tee "$EVIDENCE/firmware/tests/crypto_results.txt"
export CARBENTRA_STARTUP_TEST_BINARY="$PWD/firmware/build-host/test_startup"
export CARBENTRA_TIME_TEST_BINARY="$PWD/firmware/build-host/test_time_signature"
export CARBENTRA_CERT_TEST_BINARY="$PWD/firmware/build-host/test_certificate_dates"
python3 "$CARBENTRA_PLATFORM_ROOT/edge/tools/run_checks.py" --release --output "$EVIDENCE/firmware/evidence/shared-edge-validation.json" 2>&1 | tee "$EVIDENCE/firmware/evidence/shared-edge-results.txt"
python3 -m unittest discover -s tests/hardware -v
python3 scripts/validate_hardware_evidence.py
