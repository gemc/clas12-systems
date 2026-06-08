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
