"""Verify that firmware/edge evidence matches the delivered current source tree."""
from pathlib import Path
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[1]
record_path = R / "firmware/validation.json"
if not record_path.exists():
    raise SystemExit("Missing firmware validation record")

e = json.loads(record_path.read_text(encoding="utf-8"))
checks = []


def check(name, ok, detail=""):
    checks.append({"check": name, "passed": bool(ok), "detail": detail})


for name, digest in e.get("source_sha256", {}).items():
    f = R / name
    check(
        "source " + name,
        f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == digest,
    )

status = e.get("actual_target_build")
target = e.get("target")
artifacts = e.get("artifact_sha256", {})
check("target identity", target == "esp32c3", str(target))

if status == "PASS":
    for name, digest in artifacts.items():
        f = R / "firmware/artifacts" / name
        check(
            "binary " + name,
            f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest() == digest,
        )
    log = R / "firmware/target_build.log"
    check(
        "current target build evidence",
        bool(artifacts) and log.is_file() and "Project build complete." in log.read_text(errors="replace"),
    )
elif status == "REBUILD_REQUIRED_AFTER_BRAND_NAMESPACE_MIGRATION":
    checked_bins = list((R / "firmware/artifacts").glob("*.bin"))
    check("target rebuild explicitly pending", not artifacts and not checked_bins)
else:
    check("recognized target build state", False, str(status))

check(
    "actuation disabled",
    e.get("actuation_enabled") is False
    and "# CONFIG_CARBENTRA_ALLOW_ACTUATION is not set"
    in (R / "firmware/sdkconfig").read_text(encoding="utf-8", errors="replace"),
)
check(
    "host regression evidence",
    e.get("host_policy_cases") == 37
    and e.get("host_local_trip_invariants") == 10000,
)
check("edge evidence", e.get("edge_unit_tests") == 24)

out = {
    "scope": "Current-source hash and reproducible development evidence consistency only; not hardware verification",
    "target_build_state": status,
    "passed": all(c["passed"] for c in checks),
    "checks": checks,
}
(R / "release").mkdir(exist_ok=True)
(R / "release/firmware_evidence_checks.json").write_text(
    json.dumps(out, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(
    json.dumps(
        {
            "passed": out["passed"],
            "checks": len(checks),
            "target_build_state": status,
            "failures": [c["check"] for c in checks if not c["passed"]],
        },
        ensure_ascii=False,
        indent=2,
    )
)
sys.exit(0 if out["passed"] else 1)
