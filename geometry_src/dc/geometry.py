"""DC geometry construction."""

from pathlib import Path
import re

from pygemc import GVolume

from coatjava import generate_volumes
from variations import geometry_source_run, geometry_source_variation


REGION_RE = re.compile(r"^region(?P<region>[1-3])_s(?P<sector>[1-6])$")
SUPERLAYER_RE = re.compile(r"^sl(?P<superlayer>[1-6])_s(?P<sector>[1-6])$")


def build_dc(configuration):
    if configuration.variation == "original":
        raise SystemExit("The obsolete DC 'original' variation is intentionally not supported.")

    dc_dir = Path(__file__).resolve().parent
    source_variation = geometry_source_variation(configuration.variation)
    source_run = geometry_source_run(configuration.variation, configuration.runno)
    configuration.runno = source_run

    for volume in generate_volumes(dc_dir, source_variation, source_run):
        if build_region(configuration, volume):
            continue
        build_superlayer(configuration, volume)


def build_region(configuration, volume):
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
    gvolume.g4placement_type = "passive"
    gvolume.solid = volume.solid
    gvolume.parameters = volume.dimensions
    gvolume.color = "aa0000"
    gvolume.material = "dcgas"
    gvolume.visible = 0
    gvolume.publish(configuration)
    return True


def build_superlayer(configuration, volume):
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
    gvolume.g4placement_type = "passive"
    gvolume.solid = volume.solid
    gvolume.parameters = volume.dimensions
    gvolume.color = "99aaff"
    gvolume.material = "dcgas"
    gvolume.style = 1
    # gvolume.digitization = "dc"
    # gvolume.set_identifier("sector", sector, "superlayer", superlayer, "layer", 1, "wire", 1)
    gvolume.publish(configuration)
    return True
