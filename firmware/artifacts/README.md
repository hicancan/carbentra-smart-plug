# Target firmware artifacts

The source tree has completed the **CARBENTRA** namespace and product-identity migration. The previously checked-in ESP32-C3 binaries were built before that migration, so they were intentionally removed rather than relabeled as if they matched the current sources.

Current evidence is therefore split deliberately:

- host-side policy, protocol, feedback and meter regressions are reproducible from the current source;
- edge unit tests are reproducible from the current source;
- the ESP32-C3 target remains the intended hardware target;
- a fresh target binary must be built from the current tree in a configured ESP-IDF environment before any binary is published again.

`firmware/validation.json` records this state as `REBUILD_REQUIRED_AFTER_BRAND_NAMESPACE_MIGRATION`.

This is a digital-development repository, not a commissioning package. No checked-in binary is evidence that the device is safe to energize, switch mains loads, or deploy in the field.
