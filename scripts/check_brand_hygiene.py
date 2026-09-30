from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Tokens are intentionally assembled so this checker does not contain the
# deprecated marks as searchable literals itself.
LEGACY = [
    ("legacy English project brand", "Carbon" + "Mirror"),
    ("legacy English project brand lowercase", "carbon" + "mirror"),
    ("legacy Chinese project brand", "碳" + "镜校园"),
    ("legacy Chinese short brand", "碳" + "镜"),
    ("legacy hardware model", "CM" + "-S16"),
    ("legacy hardware model underscore", "CM" + "_S16"),
    ("legacy test identity", "CM" + "-TEST"),
    ("transitional Rev A model", "CARBENTRA" + "_S16"),
    ("transitional Rev B base model", "CARBENTRA" + "_P16_B"),
]

BINARY_SCAN_LIMIT = 128 * 1024 * 1024


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [ROOT / Path(p.decode("utf-8")) for p in result.stdout.split(b"\0") if p]


def contains_bytes(path: Path, needle: bytes) -> bool:
    if path.stat().st_size > BINARY_SCAN_LIMIT:
        return False
    overlap = max(len(needle) - 1, 0)
    tail = b""
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            block = tail + chunk
            if needle in block:
                return True
            tail = block[-overlap:] if overlap else b""
    return False


def main() -> int:
    failures: list[str] = []
    for path in tracked_files():
        rel = path.relative_to(ROOT).as_posix()
        folded = rel.casefold()
        for label, token in LEGACY:
            if token.casefold() in folded:
                failures.append(f"path: {rel} ({label})")
        if not path.is_file():
            continue
        for label, token in LEGACY:
            if contains_bytes(path, token.encode("utf-8")):
                failures.append(f"content: {rel} ({label})")

    if failures:
        print("Legacy brand tokens found:")
        for item in sorted(set(failures)):
            print(" -", item)
        return 1

    print("Brand hygiene OK: no deprecated naming found in tracked current-tree assets.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
