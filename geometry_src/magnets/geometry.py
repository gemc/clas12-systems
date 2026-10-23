"""Passive native solenoid and unchanged GEMC2 magnets CAD placements."""

from pathlib import Path
import xml.etree.ElementTree as ET

from pygemc import GVolume

from solenoid_parameters import INNER_RADII, OUTER_RADII, Z_PLANES, Z_SHIFTS, Z_START


def build_solenoid(configuration):
    volume = GVolume("solenoid")
    volume.description = "Solenoid"
    volume.material = "G4_Cu"
    volume.color = "0000ff"
    volume.style = 1
    volume.position = f"0*cm, 0.0*cm, {Z_START + Z_SHIFTS[configuration.variation]:.15g}*mm"
    volume.make_polycone(zplane=Z_PLANES, iradius=INNER_RADII, oradius=OUTER_RADII)
    volume.publish_passive(configuration)


def build_cad(configuration):
    placements = Path(__file__).resolve().parent / "cad" / f"cad_{configuration.variation}.gxml"
    for row in ET.parse(placements).getroot().findall("volume"):
        name = row.attrib["name"]
        volume = GVolume(name)
        volume.mother = row.get("mother", "root")
        volume.material = row.attrib["material"]
        volume.color = row.attrib["color"]
        volume.position = ", ".join(row.get("position", "0*mm 0*mm 0*mm").split())
        volume.rotations = [", ".join(row.get("rotation", "0*deg 0*deg 0*deg").split())]
        volume.style = 1
        if row.get("copyOf"):
            volume.copyOf = row.attrib["copyOf"]
        else:
            volume.solid = "CAD"
            volume.parameters = f"stls/{name}.stl, 1"
        volume.publish_passive(configuration)
