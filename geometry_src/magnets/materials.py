"""Beamline tungsten alloy used by the magnets CAD shields in GEMC2."""

from pygemc import GMaterial


def define_materials(configuration):
    material = GMaterial("beamline_W")
    material.description = "beamline tungsten alloy 17.6 g/cm3"
    material.density = 17.6
    material.addMaterialWithFractionalMass("G4_Fe", 0.08)
    material.addMaterialWithFractionalMass("G4_W", 0.92)
    material.publish(configuration)
