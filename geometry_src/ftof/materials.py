"""FTOF material definitions."""

from pygemc import GMaterial


def define_materials(configuration):
    scintillator = GMaterial("scintillator")
    scintillator.description = "ftof scintillator material"
    scintillator.density = 1.032
    scintillator.addNAtoms("C", 9)
    scintillator.addNAtoms("H", 10)
    scintillator.publish(configuration)
