"""Execute one engineering script inside a selected vendor Python runtime."""
from pathlib import Path
import os
import runpy
import sys

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root / "scripts"))
handles = []
for directory in os.environ.get("CARBENTRA_NATIVE_DLL_DIRS", "").split(os.pathsep):
    if directory and hasattr(os, "add_dll_directory"):
        handles.append(os.add_dll_directory(directory))
for directory in os.environ.get("CARBENTRA_NATIVE_PYTHONPATH", "").split(os.pathsep):
    if directory:
        sys.path.append(directory)
if len(sys.argv) < 2:
    raise SystemExit("Pass a script path followed by its arguments")
script = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(script.parent))
sys.argv = sys.argv[1:]
runpy.run_path(str(script), run_name="__main__")
