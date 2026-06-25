"""PCAL material definitions."""

from pygemc import GMaterial


def define_materials(configuration):
    scintillator = GMaterial("scintillator")
    scintillator.description = "pcal scintillator material"
    scintillator.density = 1.032
    scintillator.addNAtoms("C", 9)
    scintillator.addNAtoms("H", 10)
    scintillator.publish(configuration)

    lastafoam = GMaterial("LastaFoam")
    lastafoam.description = "ec foam material"
    lastafoam.density = 0.24
    lastafoam.addMaterialWithFractionalMass("G4_C", 0.4045)
    lastafoam.addMaterialWithFractionalMass("G4_H", 0.0786)
    lastafoam.addMaterialWithFractionalMass("G4_N", 0.1573)
    lastafoam.addMaterialWithFractionalMass("G4_O", 0.3596)
    lastafoam.publish(configuration)
