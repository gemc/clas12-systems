"""EC geometry construction.

The EC builder gets all volume dimensions from the local coatjava bridge and
applies the detector metadata from the GEMC2 `geometry_java.pl` wrapper.
"""

from pathlib import Path
import re

from pygemc import GVolume

from coatjava import generate_volumes


EC_RE = re.compile(r"^ec_s(?P<sector>[1-6])$")
LID_RE = re.compile(r"^eclid(?P<lid>[1-3])_s(?P<sector>[1-6])$")
LEAD_RE = re.compile(
    r"^lead_(?P<layer>\d+)_s(?P<sector>[1-6])_view_(?P<view>[1-3])_stack_(?P<stack>[1-2])$"
)
SCINT_RE = re.compile(
    r"^(?P<uvw>[UVW])-scintillator_(?P<layer>\d+)_s(?P<sector>[1-6])"
    r"_view_(?P<view>[1-3])_stack_(?P<stack>[1-2])$"
)
STRIP_RE = re.compile(
    r"^(?P<uvw>[UVW])_strip_(?P<layer>\d+)_(?P<strip>\d+)_s(?P<sector>[1-6])"
    r"_stack_(?P<stack>[1-2])$"
)

LID_DESCRIPTION = {
    1: "Stainless Steel Skin 1",
    2: "Last-a-Foam",
    3: "Stainless Steel Skin 2",
}
LID_COLOR = {
    1: "FCFFF0",
    2: "EED18C",
    3: "FCFFF0",
}
LID_MATERIAL = {
    1: "G4_STAINLESS-STEEL",
    2: "LastaFoam",
    3: "G4_STAINLESS-STEEL",
}
SCINTILLATOR_COLOR = {
    "U": "ff6633",
    "V": "33ffcc",
    "W": "33ffcc",
}
STRIP_COLOR = {
    "U": "ff6633",
    "V": "6600ff",
    "W": "6600ff",
}
VIEW_BY_UVW = {
    "U": 1,
    "V": 2,
    "W": 3,
}


def build_ec(configuration):
    """Publish all EC volumes for the variation currently selected in configuration."""
    ec_dir = Path(__file__).resolve().parent
    for volume in generate_volumes(ec_dir, configuration.variation, configuration.runno):
        publish_ec_volume(configuration, volume)


def publish_ec_volume(configuration, volume):
    """Publish one EC coatjava volume after applying GEMC2 metadata."""
    gvolume = base_volume(volume)

    if match := EC_RE.match(volume.name):
        sector = int(match.group("sector"))
        gvolume.description = f"Forward Calorimeter - Sector {sector}"
        gvolume.color = "ff1111"
        gvolume.material = "G4_AIR"
        gvolume.visible = 0
    elif match := LID_RE.match(volume.name):
        lid = int(match.group("lid"))
        gvolume.description = LID_DESCRIPTION[lid]
        gvolume.color = LID_COLOR[lid]
        gvolume.material = LID_MATERIAL[lid]
        gvolume.style = 1
    elif match := LEAD_RE.match(volume.name):
        layer = int(match.group("layer"))
        gvolume.description = f"Forward Calorimeter lead layer {layer}"
        gvolume.color = "7CFC00"
        gvolume.material = "G4_Pb"
        gvolume.style = 1
    elif match := SCINT_RE.match(volume.name):
        uvw = match.group("uvw")
        layer = int(match.group("layer"))
        gvolume.description = f"Forward Calorimeter scintillator layer {layer}"
        gvolume.color = SCINTILLATOR_COLOR[uvw]
        gvolume.material = "G4_AIR"
        gvolume.style = 0
    elif match := STRIP_RE.match(volume.name):
        uvw = match.group("uvw")
        scintillator_layer = int(match.group("layer"))
        sector = int(match.group("sector"))
        stack = int(match.group("stack"))
        strip = int(match.group("strip"))
        view = VIEW_BY_UVW[uvw]
        hipo_layer = view + stack * 3

        gvolume.description = (
            f"Forward Calorimeter scintillator layer {scintillator_layer} strip {strip} view {view}"
        )
        gvolume.color = STRIP_COLOR[uvw]
        gvolume.material = "scintillator"
        gvolume.style = 1
        gvolume.digitization = "ecal"
        gvolume.set_identifier("sector", sector, "layer", hipo_layer, "strip", strip)
    else:
        raise ValueError(f"Unexpected EC coatjava volume name: {volume.name}")

    gvolume.publish(configuration)


def base_volume(volume):
    """Return a GVolume with the common placement and solid fields populated."""
    gvolume = GVolume(volume.name)
    gvolume.mother = volume.mother
    gvolume.position = volume.position
    gvolume.rotations = [volume.rotation]
    gvolume.g4placement_type = "passive"
    gvolume.solid = volume.solid
    gvolume.parameters = volume.dimensions
    return gvolume
