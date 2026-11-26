"""The built package must include every file that the exports read from braiid/.

The exports find these files next to the installed rsm package, so a file that the
package config leaves out is missing for everyone who installs RSM.
"""

import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent

# HTML output inlines or copies braiid.css. LaTeX and PDF export pass braiid.lua and
# theorems.tex to pandoc, and LaTeX export copies braiid.sty next to the output.
EXPORT_FILES = [
    "braiid/braiid.css",
    "braiid/braiid.lua",
    "braiid/theorems.tex",
    "braiid/braiid.sty",
]


@pytest.mark.skipif(shutil.which("uv") is None, reason="uv not installed")
def test_wheel_includes_export_files(tmp_path):
    subprocess.run(
        ["uv", "build", "--wheel", "--out-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        check=True,
    )
    (wheel,) = tmp_path.glob("*.whl")
    names = set(zipfile.ZipFile(wheel).namelist())
    missing = [f for f in EXPORT_FILES if f not in names]
    assert not missing
