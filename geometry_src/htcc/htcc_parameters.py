"""Loader for the static HTCC geometry parameters.

Unlike LTCC, the HTCC shape parameters (mirror ellipse semi-axes, focal points,
dividing-plane points and barrel geometry) are hand-authored constants, checked in
verbatim from `clas12Tags/geometry_source/htcc/htcc__parameters_default.txt`. There is
no ROOT macro to regenerate them; the file is read as-is and the values are kept as
floats for the geometry math (the perl `mirrors.pl` interpolates them numerically).
"""

from pathlib import Path

HTCC_DIR = Path(__file__).resolve().parent


def load_parameters(variation="default"):
    """Return the {name: float} parameter map read from the checked-in parameters file."""
    parameters_file = HTCC_DIR / "htcc__parameters_default.txt"

    parameters = {}
    for line in parameters_file.read_text(encoding="utf-8").splitlines():
        fields = line.split("|")
        if len(fields) < 2:
            continue
        name = fields[0].strip()
        if not name:
            continue
        parameters[name] = float(fields[1].strip())
    return parameters
