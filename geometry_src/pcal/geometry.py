"""PCAL geometry construction.

The PCAL builder gets all volume dimensions from the local coatjava bridge and
applies the detector metadata from the GEMC2 `geometry_java.pl` wrapper.
"""

import math
from pathlib import Path
import re

from pygemc import GVolume

from coatjava import generate_volumes


MOTHER_RE = re.compile(r"^pcal_s(?P<sector>[1-6])$")
LEAD_RE = re.compile(r"^PCAL_Lead_Layer_(?P<layer>\d+)_s(?P<sector>[1-6])$")
SCINTILLATOR_RE = re.compile(r"^(?P<uvw>[UVW])-view-scintillator_(?P<layer>\d+)_s(?P<sector>[1-6])$")
STRIP_RE = re.compile(
    r"^(?P<uvw>[UVW])-view_(?P<kind>single|double)_strip_"
    r"(?P<view>\d+)_(?P<strip>\d+)_s(?P<sector>[1-6])$"
)
STEEL_RE = re.compile(r"^Stainless_Steel_(?P<side>Front|Back)_(?P<copy>[1-2])_s(?P<sector>[1-6])$")
FOAM_RE = re.compile(r"^Last-a-Foam_(?P<side>Front|Back)_s(?P<sector>[1-6])$")

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
LAYER_BY_UVW = {
    "U": 1,
    "V": 2,
    "W": 3,
}


def build_pcal(configuration):
    """Publish all PCAL volumes for the variation currently selected in configuration."""
    pcal_dir = Path(__file__).resolve().parent
    for volume in generate_volumes(pcal_dir, configuration.variation, configuration.runno):
        if build_mother(configuration, volume):
            continue
        if build_lead_layer(configuration, volume):
            continue
        if build_scintillator_layer(configuration, volume):
            continue
        if build_strip(configuration, volume):
            continue
        if build_steel_window(configuration, volume):
            continue
        if build_foam_window(configuration, volume):
            continue

        raise ValueError(f"Unexpected PCAL coatjava volume name: {volume.name}")


def build_mother(configuration, volume):
    """Publish one PCAL sector mother volume, returning False for non-mother rows."""
    if not MOTHER_RE.match(volume.name):
        return False

    gvolume = base_volume(volume)
    gvolume.description = "Preshower Calorimeter"
    gvolume.color = "ff1111"
    gvolume.material = "G4_AIR"
    gvolume.visible = 0
    gvolume.publish(configuration)
    return True


def build_lead_layer(configuration, volume):
    """Publish one PCAL lead layer volume, returning False for non-lead rows."""
    match = LEAD_RE.match(volume.name)
    if not match:
        return False

    layer = int(match.group("layer"))
    gvolume = base_volume(volume)
    gvolume.description = f"Preshower Calorimeter lead layer {layer}"
    gvolume.color = "66ff33"
    gvolume.material = "G4_Pb"
    gvolume.style = 1
    gvolume.publish(configuration)
    return True


def build_scintillator_layer(configuration, volume):
    """Publish one PCAL scintillator layer mother volume, returning False for non-scintillator rows."""
    match = SCINTILLATOR_RE.match(volume.name)
    if not match:
        return False

    uvw = match.group("uvw")
    gvolume = base_volume(volume)
    gvolume.description = "Preshower Calorimeter"
    gvolume.color = SCINTILLATOR_COLOR[uvw]
    gvolume.material = "G4_TITANIUM_DIOXIDE"
    gvolume.publish(configuration)
    return True


def build_strip(configuration, volume):
    """Publish one PCAL strip volume, returning False for non-strip rows."""
    match = STRIP_RE.match(volume.name)
    if not match:
        return False

    kind = match.group("kind")
    uvw = match.group("uvw")
    sector = int(match.group("sector"))
    strip = int(match.group("strip"))
    layer = LAYER_BY_UVW[uvw]

    gvolume = base_volume(volume)
    gvolume.description = f"Preshower Calorimeter scintillator layer {layer} strip"
    gvolume.color = STRIP_COLOR[uvw]
    gvolume.material = "scintillator"
    gvolume.style = 1

    if strip > 0:
        gvolume.digitization = "ecal"
        gvolume.set_identifier("sector", sector, "layer", layer, "strip", pcal_strip_id(uvw, kind, strip))

    gvolume.publish(configuration)
    return True


def build_steel_window(configuration, volume):
    """Publish one PCAL stainless-steel front/back window, returning False for other rows."""
    match = STEEL_RE.match(volume.name)
    if not match:
        return False

    side = match.group("side")
    gvolume = base_volume(volume)
    gvolume.description = f"{side} Window"
    gvolume.color = "D4E3EE"
    gvolume.material = "G4_STAINLESS-STEEL"
    gvolume.style = 1
    gvolume.publish(configuration)
    return True


def build_foam_window(configuration, volume):
    """Publish one PCAL Last-a-Foam front/back window, returning False for other rows."""
    match = FOAM_RE.match(volume.name)
    if not match:
        return False

    side = match.group("side")
    gvolume = base_volume(volume)
    gvolume.description = f"{side} Foam"
    gvolume.color = "EED18C"
    gvolume.material = "LastaFoam"
    gvolume.style = 1
    gvolume.publish(configuration)
    return True


def pcal_strip_id(uvw, kind, strip):
    """Return the GEMC2 strip identifier for a PCAL raw strip volume number."""
    if kind == "double":
        if uvw == "U":
            return strip + 52
        return strip

    if uvw == "U":
        nsingles = 52
        if strip <= nsingles:
            return strip
        return math.ceil((strip - nsingles) / 2) + nsingles

    ndoubles = 30
    ncouples = ndoubles // 2
    if strip > ndoubles:
        return strip - ncouples
    return math.ceil(strip / 2)


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
