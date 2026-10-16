"""Run mappings from clas12Tags/geometry_source/beamline/beamline.pl."""

from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parents[1]))
from clas12_common import BEAMLINE_CUSTOM_START


variation_to_run = {
    "default": 11,
    "rga_spring2018": 3029,
    "rgk_winter2018": 5874,
    "rgb_spring2019": 6150,
    "rgf_spring2020": 11620,
    "rgc_summer2022": 16000,
    "rgd_fall2023": 18304,
    "rgl_spring2025": 21000,
    "rgc_fall2022": 16843,
    "rge_spring2024": 20000,
}

custom_variation_to_run = {
    name: BEAMLINE_CUSTOM_START + index
    for index, name in enumerate(("ddvcs", "rghFTOut", "rghFTOn", "TransverseUpstreamBeampipe", "elmo7"))
}

# Keep the existing no-wedge and ELMO runs; reserve two unused keys for the other CAD alternatives.
transverse_variation_to_run = {
    "noWedges": custom_variation_to_run["TransverseUpstreamBeampipe"],
    "forwardWedges": BEAMLINE_CUSTOM_START + 5,
    "midpointWedges": BEAMLINE_CUSTOM_START + 6,
}
