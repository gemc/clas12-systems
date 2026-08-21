"""DC geometry construction.

The DC builder gets the chamber region and superlayer solids from the local
coatjava bridge, converts them to GEMC3 volumes, and adds detector-specific
custom geometry where needed.
"""

import math
import sys
from pathlib import Path
import re

from pygemc import GVolume

sys.path.insert(0, str(Path(__file__).parent.parent))
from clas12_common import gemc2_fstr
from coatjava import generate_volumes
from variations import variation_to_run


REGION_RE = re.compile(r"^region(?P<region>[1-3])_s(?P<sector>[1-6])$")
SUPERLAYER_RE = re.compile(r"^sl(?P<superlayer>[1-6])_s(?P<sector>[1-6])$")
DDVCS_SHIELD_X_CENTER = 227.2394445
DDVCS_SHIELD_Z_CENTER = 457.3735853
DDVCS_SHIELD_HALF_LENGTH_Z = 16.6
DDVCS_SHIELD_Z_ALLOWANCE = 8.0


def build_dc(configuration):
    """Publish all DC volumes for the variation currently selected in configuration."""
    dc_dir = Path(__file__).resolve().parent
    source_variation = configuration.variation
    source_run = configuration.runno

    # DDVCS reuses the default DC chamber geometry and adds a custom region-3 shield below.
    if configuration.variation == "ddvcs":
        source_variation = "default"
        source_run = variation_to_run["default"]

    for volume in generate_volumes(dc_dir, source_variation, source_run):
        if build_region(configuration, volume):
            continue
        build_superlayer(configuration, volume)

    if configuration.variation == "ddvcs":
        build_ddvcs_back_shields(configuration)


def build_region(configuration, volume):
    """Publish one coatjava region mother volume, returning False for non-region rows."""
    match = REGION_RE.match(volume.name)
    if not match:
        return False

    region = int(match.group("region"))
    sector = int(match.group("sector"))

    gvolume = GVolume(volume.name)
    gvolume.mother = volume.mother
    gvolume.description = f"CLAS12 Drift Chambers, Sector {sector} Region {region}"
    gvolume.position = volume.position
    gvolume.rotations = [volume.rotation]
    gvolume.solid = volume.solid
    gvolume.parameters = volume.dimensions
    gvolume.color = "aa0000"
    gvolume.material = "dcgas"
    gvolume.visible = 0
    gvolume.publish_passive(configuration)
    return True


def build_superlayer(configuration, volume):
    """Publish one coatjava superlayer volume, returning False for non-superlayer rows."""
    match = SUPERLAYER_RE.match(volume.name)
    if not match:
        return False

    superlayer = int(match.group("superlayer"))
    sector = int(match.group("sector"))
    region = ((superlayer - 1) // 2) + 1

    gvolume = GVolume(volume.name)
    gvolume.mother = volume.mother
    gvolume.description = f"Region {region}, Super Layer {superlayer}, Sector {sector}"
    gvolume.position = volume.position
    gvolume.rotations = [volume.rotation]
    gvolume.solid = volume.solid
    gvolume.parameters = volume.dimensions
    gvolume.color = "99aaff"
    gvolume.material = "dcgas"
    gvolume.style = 1
    gvolume.digitization = "dc"
    gvolume.set_identifier("sector", sector, "superlayer", superlayer, "layer", 1, "wire", 1)
    gvolume.publish_passive(configuration)
    return True


def build_ddvcs_back_shields(configuration):
    """Publish the six graphite DDVCS back-shield volumes from GEMC2 region3_shield.pl."""
    y_enlargement = 1.0
    dx_shift = float(gemc2_fstr(y_enlargement * math.tan(math.radians(29.5))))
    # GEMC2 defines these shields as thin G4Trap plates in the global CLAS12 frame.
    dimensions = ", ".join(
        [
            "2*mm",
            "-25*deg",
            "90*deg",
            f"{216.109 + y_enlargement}*cm",
            f"{8.8578648 - dx_shift}*cm",
            f"{229.84 + dx_shift}*cm",
            "0*deg",
            f"{216.109 + y_enlargement}*cm",
            f"{8.8578648 - dx_shift}*cm",
            f"{229.84 + dx_shift}*cm",
            "0*deg",
        ]
    )

    for sector in range(1, 7):
        # Rotate the region-3 sector-1 center around z to match CLAS12 sector placement.
        phi = -(sector - 1) * 60
        x = DDVCS_SHIELD_X_CENTER * math.cos(math.radians(phi))
        y = -DDVCS_SHIELD_X_CENTER * math.sin(math.radians(phi))
        z = DDVCS_SHIELD_Z_CENTER + DDVCS_SHIELD_HALF_LENGTH_Z + DDVCS_SHIELD_Z_ALLOWANCE

        gvolume = GVolume(f"back_shielding_region3_s{sector}")
        gvolume.mother = "root"
        gvolume.description = f"CLAS12 Drift Chamber Sheildings for DDVCS, Sector {sector} Region 3"
        gvolume.position = f"{gemc2_fstr(x)}*cm, {gemc2_fstr(y)}*cm, {gemc2_fstr(z)}*cm"
        gvolume.rotations = [f"ordered: zxy, {90 - (sector - 1) * 60}*deg, 25*deg, 0*deg"]
        gvolume.solid = "G4Trap"
        gvolume.parameters = dimensions
        gvolume.color = "555599"
        gvolume.material = "G4_GRAPHITE"
        gvolume.style = 1
        gvolume.publish_passive(configuration)
