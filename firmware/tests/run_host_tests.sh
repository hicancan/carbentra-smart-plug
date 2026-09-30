#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build-host
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/cm_policy.c tests/test_policy.c -o build-host/test_policy
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_policy
SDK="${IDF_PATH:-../../sdk/esp-idf}"
[ -f "$SDK/components/json/cJSON/cJSON.c" ] || { echo "Set IDF_PATH to an installed official ESP-IDF checkout" >&2; exit 1; }
cc -std=c11 -Wall -Wextra -Werror -g -O1 -fsanitize=undefined,address -Icore -I"$SDK/components/json/cJSON" core/cm_command_json.c core/cm_meter_decode.c "$SDK/components/json/cJSON/cJSON.c" tests/test_protocol.c -lm -o build-host/test_protocol
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_protocol
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/cm_feedback.c tests/test_feedback.c -o build-host/test_feedback
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_feedback
