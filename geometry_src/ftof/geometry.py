"""FTOF geometry construction.

The FTOF builder gets all volume dimensions from the local coatjava bridge and
applies the detector metadata from the GEMC2 `geometry_java.pl` wrapper.

The modern `FTOFGeant4Factory` emits three families of volumes:

* panel mothers   ``ftof_p{1a,1b,2}_s{sector}``                  (air, invisible)
* scintillator    ``panel{1a,1b,2}_sector{sector}_paddle_{n}``   (sensitive paddles)
* lead shields    ``ftof_shield_p{1a,2}_sector{sector}``         (Pb, panels 1a and 2 only)
"""

from pathlib import Path
import re

from pygemc import GVolume

from coatjava import generate_volumes


PANEL_RE = re.compile(r"^ftof_p(?P<panel>1a|1b|2)_s(?P<sector>[1-6])$")
PADDLE_RE = re.compile(
    r"^panel(?P<panel>1a|1b|2)_sector(?P<sector>[1-6])_paddle_(?P<paddle>\d+)$"
)
SHIELD_RE = re.compile(r"^ftof_shield_p(?P<panel>1a|2)_sector(?P<sector>[1-6])$")

# GEMC2 hipo panel index: panel 1a -> 1, panel 1b -> 2, panel 2 -> 3.
PANEL_TO_LAYER = {"1a": 1, "1b": 2, "2": 3}

PADDLE_COLOR = {
    "1a": "ff11aa",
    "1b": "11ffaa",
    "2": "ff11aa",
}


def build_ftof(configuration):
    """Publish all FTOF volumes for the variation currently selected in configuration."""
    ftof_dir = Path(__file__).resolve().parent
    for volume in generate_volumes(ftof_dir, configuration.variation, configuration.runno):
        publish_ftof_volume(configuration, volume)


def publish_ftof_volume(configuration, volume):
    """Publish one FTOF coatjava volume after applying GEMC2 metadata."""
    gvolume = base_volume(volume)

    if match := PANEL_RE.match(volume.name):
        panel = match.group("panel")
        sector = int(match.group("sector"))
        gvolume.description = f"Forward TOF - Panel {panel} - Sector {sector}"
        gvolume.color = "000000"
        gvolume.material = "G4_AIR"
        gvolume.visible = 0
        gvolume.style = 0
    elif match := PADDLE_RE.match(volume.name):
        panel = match.group("panel")
        sector = int(match.group("sector"))
        paddle = int(match.group("paddle"))
        layer = PANEL_TO_LAYER[panel]

        gvolume.description = f"paddle {paddle} - Panel {panel} - Sector {sector}"
        gvolume.color = PADDLE_COLOR[panel]
        gvolume.material = "scintillator"
        gvolume.style = 1
        gvolume.digitization = "ftof"
        gvolume.set_identifier("sector", sector, "panel", layer, "paddle", paddle, "side", 0)
    elif match := SHIELD_RE.match(volume.name):
        panel = match.group("panel")
        sector = int(match.group("sector"))
        gvolume.description = f"Layer of lead - layer {panel} - Sector {sector}"
        gvolume.color = "dc143c"
        gvolume.material = "G4_Pb"
        gvolume.style = 1
    else:
        raise ValueError(f"Unexpected FTOF coatjava volume name: {volume.name}")

    gvolume.publish_passive(configuration)


def base_volume(volume):
    """Return a GVolume with the common placement and solid fields populated."""
    gvolume = GVolume(volume.name)
    gvolume.mother = volume.mother
    gvolume.position = volume.position
    gvolume.rotations = [volume.rotation]
    gvolume.solid = volume.solid
    gvolume.parameters = volume.dimensions
    return gvolume
