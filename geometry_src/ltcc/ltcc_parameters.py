"""Loader for the LTCC mirror parameters produced by `root -q -b mirrors.C`.

The mirror shapes (ellipse and hyperbola implicit-equation coefficients, span points,
PMT/WC/shield placements) are calculated by the ROOT macro `mirrors.C` with its
`utils/` sources and `parameters/` data files, all copied verbatim from
`clas12Tags/geometry_source/ltcc`. The macro writes `ltcc__parameters_default.txt`,
which is checked in; it is regenerated automatically here when missing, exactly as
`clas12Tags/create_geometry.sh` does before running the perl scripts.
"""

from pathlib import Path
import shutil
import subprocess
import sys

LTCC_DIR = Path(__file__).resolve().parent


def load_parameters(variation="default"):
    """Return the {name: value} parameter map, with values kept as raw strings."""
    parameters_file = LTCC_DIR / f"ltcc__parameters_{variation}.txt"
    if not parameters_file.exists():
        generate_parameters()

    parameters = {}
    for line in parameters_file.read_text(encoding="utf-8").splitlines():
        fields = line.split("|")
        if len(fields) < 2:
            continue
        parameters[fields[0].strip()] = fields[1].strip()
    return parameters


def generate_parameters():
    """Run `root -q -b mirrors.C` in this directory to (re)create the parameters file."""
    if shutil.which("root") is None:
        sys.exit(
            "LTCC parameters file is missing and ROOT is not available.\n"
            "Run 'root -q -b mirrors.C' inside geometry_src/ltcc to generate it."
        )
    subprocess.run(["root", "-q", "-b", "mirrors.C"], cwd=LTCC_DIR, check=True)
