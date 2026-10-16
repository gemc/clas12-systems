"""Beamline materials from clas12Tags/geometry_source/beamline/materials.pl."""

from pygemc import GMaterial


def define_materials(configuration):
    for name, description, density, components in (
        ("beamline_W", "beamline tungsten alloy 17.6 g/cm3", 17.6,
         (("G4_Fe", 0.08), ("G4_W", 0.92))),
        ("beamline_CarbonSteel", "beamline carbon steel ASTM A36 7.85 g/cm3", 7.85,
         (("G4_Fe", 0.98), ("G4_C", 0.003), ("G4_Si", 0.002),
          ("G4_Mn", 0.01), ("G4_P", 0.003), ("G4_Cu", 0.002))),
    ):
        material = GMaterial(name)
        material.description = description
        material.density = density
        for component, fraction in components:
            material.addMaterialWithFractionalMass(component, fraction)
        material.publish(configuration)
