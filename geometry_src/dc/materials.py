"""DC material definitions."""

from pygemc import GMaterial


def define_materials(configuration):
    dcgas = GMaterial("dcgas")
    dcgas.description = "clas12 dc gas"
    dcgas.density = 0.0018
    dcgas.addMaterialWithFractionalMass("G4_Ar", 0.9)
    dcgas.addMaterialWithFractionalMass("G4_CARBON_DIOXIDE", 0.1)
    dcgas.publish(configuration)

    tungsten_alloy = GMaterial("W_alloy")
    tungsten_alloy.description = "tungsten alloy 17.6 g/cm3"
    tungsten_alloy.density = 17.6
    tungsten_alloy.addMaterialWithFractionalMass("G4_Fe", 0.08)
    tungsten_alloy.addMaterialWithFractionalMass("G4_W", 0.92)
    tungsten_alloy.publish(configuration)
