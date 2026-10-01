#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p build-host
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/carbentra_policy.c tests/test_policy.c -o build-host/test_policy
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_policy
SDK="${IDF_PATH:-../../sdk/esp-idf}"
JSON_DIR="$SDK/components/json/cJSON"
if [ ! -f "$JSON_DIR/cJSON.c" ]; then JSON_DIR="third_party/cJSON"; fi
[ -f "$JSON_DIR/cJSON.c" ] || { echo "Missing cJSON test dependency" >&2; exit 1; }
cc -std=c11 -Wall -Wextra -Werror -g -O1 -fsanitize=undefined,address -Icore -I"$JSON_DIR" core/carbentra_command_json.c core/carbentra_json.c core/carbentra_meter_decode.c "$JSON_DIR/cJSON.c" tests/test_protocol.c -lm -o build-host/test_protocol
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_protocol
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/carbentra_feedback.c tests/test_feedback.c -o build-host/test_feedback
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_feedback
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore -Imain -Itests/mocks main/carbentra_storage.c tests/test_storage.c -o build-host/test_storage
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_storage
cc -std=c11 -Wall -Wextra -Werror -pedantic -g -O1 -fsanitize=undefined,address -Icore core/carbentra_calibration.c core/carbentra_meter_decode.c core/carbentra_execution.c tests/test_calibration_execution.c -lm -o build-host/test_calibration_execution
ASAN_OPTIONS=detect_leaks=0 ./build-host/test_calibration_execution
cc -std=c11 -Wall -Wextra -Werror -g -O1 -fsanitize=undefined,address -Icore -Imain -Itests/mocks -I"$JSON_DIR" main/carbentra_storage.c core/carbentra_policy.c core/carbentra_feedback.c core/carbentra_execution.c "$JSON_DIR/cJSON.c" tests/test_startup.c -lm -o build-host/test_startup
for fail in 0 1 2 3 4 5 6; do ASAN_OPTIONS=detect_leaks=0 ./build-host/test_startup "$fail"; done
