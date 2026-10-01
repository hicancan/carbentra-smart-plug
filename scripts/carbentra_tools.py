"""Tool-owned native runtimes and portable resources for engineering scripts.

Run native scripts through engineering.ps1. Plain report/test utilities use uv.
No global interpreter, environment variables or vendor installation is modified.
"""
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
KICAD_SHARE = Path(os.environ.get("CARBENTRA_KICAD_SHARE", "/usr/share/kicad"))
FREECAD_LIB = os.environ.get("CARBENTRA_FREECAD_LIB", "/usr/lib/freecad-python3/lib")
FONT_REGULAR = str(ROOT / "assets/fonts/NotoSansSC-Regular.ttf")
PYTHON = sys.executable


def kicad_resource(relative: str) -> str:
    return str(KICAD_SHARE / relative)
