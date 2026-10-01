#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${MBEDTLS_INCLUDE:?Point to verified mbedTLS include directory}"
: "${MBEDTLS_CRYPTO_LIBRARY:?Point to verified host libmbedcrypto.a}"
: "${CARBENTRA_PLATFORM_ROOT:?Set the explicit path to the sole platform Edge checkout}"
test -f "$CARBENTRA_PLATFORM_ROOT/edge/tests/test_time_bootstrap.py"
mkdir -p build-host
cc -std=c11 -Wall -Wextra -Werror -O1 -g -fsanitize=address,undefined -Icore -Ithird_party/cJSON -I"$MBEDTLS_INCLUDE" core/carbentra_time_signature.c core/carbentra_json.c third_party/cJSON/cJSON.c tests/test_time_signature.c "$MBEDTLS_CRYPTO_LIBRARY" -lm -o build-host/test_time_signature
CARBENTRA_TIME_TEST_BINARY="$PWD/build-host/test_time_signature" python3 -m pytest "$CARBENTRA_PLATFORM_ROOT/edge/tests/test_time_bootstrap.py" -v
MBEDTLS_X509_LIBRARY="${MBEDTLS_X509_LIBRARY:-$(dirname "$MBEDTLS_CRYPTO_LIBRARY")/libmbedx509.a}"
cc -std=c11 -Wall -Wextra -Werror -O1 -g -fsanitize=address,undefined -I"$MBEDTLS_INCLUDE" tests/test_certificate_dates.c "$MBEDTLS_X509_LIBRARY" "$MBEDTLS_CRYPTO_LIBRARY" -lm -o build-host/test_certificate_dates
CARBENTRA_CERT_TEST_BINARY="$PWD/build-host/test_certificate_dates" python3 -m pytest "$CARBENTRA_PLATFORM_ROOT/edge/tests/test_certificate_dates.py" -v
