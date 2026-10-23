"""Local CLAS12 run and variation mapping used by the DC geometry builder."""

from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parents[1]))
from clas12_common import DC_CUSTOM_START


variation_to_run = {
    "default": 11,
}

custom_variation_to_run = {
    "ddvcs": DC_CUSTOM_START,
}

# Preserve exact CAD run keys from the magnets banks these membranes previously belonged to.
cad_variation_to_run = {
    **variation_to_run,
    "rga_spring2018": 3029,
    "rga_fall2018": 4763,
    **custom_variation_to_run,
}
