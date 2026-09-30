#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build-host
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/cm_policy.c tests/test_policy.c -o build-host/test_policy
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_policy
SDK="${IDF_PATH:-../../sdk/esp-idf}"
JSON_DIR="$SDK/components/json/cJSON"
if [ ! -f "$JSON_DIR/cJSON.c" ]; then JSON_DIR="third_party/cJSON"; fi
[ -f "$JSON_DIR/cJSON.c" ] || { echo "Missing cJSON test dependency" >&2; exit 1; }
cc -std=c11 -Wall -Wextra -Werror -g -O1 -fsanitize=undefined,address -Icore -I"$JSON_DIR" core/cm_command_json.c core/cm_meter_decode.c "$JSON_DIR/cJSON.c" tests/test_protocol.c -lm -o build-host/test_protocol
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_protocol
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/cm_feedback.c tests/test_feedback.c -o build-host/test_feedback
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_feedback
