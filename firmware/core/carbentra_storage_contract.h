#pragma once
/* Stable on-flash identifiers are protocol, not display branding. No deployed
 * units exist in this development release. Incompatible calibration is rejected,
 * never guessed or erased. Future migrations require a reviewed explicit tool. */
#define CARBENTRA_NVS_JOURNAL "cb_journal"
#define CARBENTRA_NVS_FACTORY "cb_factory"
#define CARBENTRA_NVS_SECURE "cb_secure"
#define CARBENTRA_BOARD_REVISION "CARBENTRA-P16-EVT-B"
#define CARBENTRA_WIRE_VERSION 2
_Static_assert(sizeof(CARBENTRA_NVS_JOURNAL) <= 16, "NVS namespace exceeds 15 bytes");
_Static_assert(sizeof(CARBENTRA_NVS_FACTORY) <= 16, "NVS namespace exceeds 15 bytes");
_Static_assert(sizeof(CARBENTRA_NVS_SECURE) <= 16, "NVS namespace exceeds 15 bytes");
