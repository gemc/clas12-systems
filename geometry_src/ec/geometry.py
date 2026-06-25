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
        if build_mother(configuration, volume):
            continue
        if build_lid(configuration, volume):
            continue
        if build_lead_layer(configuration, volume):
            continue
        if build_scintillator_layer(configuration, volume):
            continue
        if build_strip(configuration, volume):
            continue

        raise ValueError(f"Unexpected EC coatjava volume name: {volume.name}")


def build_mother(configuration, volume):
    """Publish one EC sector mother volume, returning False for non-mother rows."""
    match = EC_RE.match(volume.name)
    if not match:
        return False

    sector = int(match.group("sector"))
    gvolume = base_volume(volume)
    gvolume.description = f"Forward Calorimeter - Sector {sector}"
    gvolume.color = "ff1111"
    gvolume.material = "G4_AIR"
    gvolume.visible = 0
    gvolume.publish(configuration)
    return True


def build_lid(configuration, volume):
    """Publish one EC cover/lastafoam lid volume, returning False for non-lid rows."""
    match = LID_RE.match(volume.name)
    if not match:
        return False

    lid = int(match.group("lid"))
    gvolume = base_volume(volume)
    gvolume.description = LID_DESCRIPTION[lid]
    gvolume.color = LID_COLOR[lid]
    gvolume.material = LID_MATERIAL[lid]
    gvolume.style = 1
    gvolume.publish(configuration)
    return True


def build_lead_layer(configuration, volume):
    """Publish one EC lead layer volume, returning False for non-lead rows."""
    match = LEAD_RE.match(volume.name)
    if not match:
        return False

    layer = int(match.group("layer"))
    gvolume = base_volume(volume)
    gvolume.description = f"Forward Calorimeter lead layer {layer}"
    gvolume.color = "7CFC00"
    gvolume.material = "G4_Pb"
    gvolume.style = 1
    gvolume.publish(configuration)
    return True


def build_scintillator_layer(configuration, volume):
    """Publish one EC scintillator layer mother volume, returning False for non-scintillator rows."""
    match = SCINT_RE.match(volume.name)
    if not match:
        return False

    uvw = match.group("uvw")
    layer = int(match.group("layer"))
    gvolume = base_volume(volume)
    gvolume.description = f"Forward Calorimeter scintillator layer {layer}"
    gvolume.color = SCINTILLATOR_COLOR[uvw]
    gvolume.material = "G4_AIR"
    gvolume.style = 0
    gvolume.publish(configuration)
    return True


def build_strip(configuration, volume):
    """Publish one EC sensitive strip volume, returning False for non-strip rows."""
    match = STRIP_RE.match(volume.name)
    if not match:
        return False

    uvw = match.group("uvw")
    scintillator_layer = int(match.group("layer"))
    sector = int(match.group("sector"))
    stack = int(match.group("stack"))
    strip = int(match.group("strip"))
    view = VIEW_BY_UVW[uvw]
    hipo_layer = view + stack * 3

    gvolume = base_volume(volume)
    gvolume.description = (
        f"Forward Calorimeter scintillator layer {scintillator_layer} strip {strip} view {view}"
    )
    gvolume.color = STRIP_COLOR[uvw]
    gvolume.material = "scintillator"
    gvolume.style = 1
    gvolume.digitization = "ecal"
    gvolume.set_identifier("sector", sector, "layer", hipo_layer, "strip", strip)
    gvolume.publish(configuration)
    return True


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
