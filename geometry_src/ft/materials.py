"""Forward Tagger material definitions ported from clas12Tags."""

from pygemc import GMaterial


def material(configuration, name, description, density, atoms=(), fractions=()):
    """Publish one material using atomic counts or fractional masses."""
    gmaterial = GMaterial(name)
    gmaterial.description = description
    gmaterial.density = density
    for component, amount in atoms:
        gmaterial.addNAtoms(component, amount)
    for component, fraction in fractions:
        gmaterial.addMaterialWithFractionalMass(component, fraction)
    gmaterial.publish(configuration)


def define_materials(configuration):
    """Publish the fourteen custom materials used by FTCAL, FTHODO, and FTTRK."""
    material(
        configuration,
        "ft_peek",
        "ft peek plastic 1.31 g/cm3",
        1.31,
        fractions=(("G4_C", 0.76), ("G4_H", 0.08), ("G4_O", 0.16)),
    )
    material(
        configuration,
        "ft_W",
        "ft tungsten alloy 17.6 g/cm3",
        17.6,
        fractions=(("G4_Fe", 0.08), ("G4_W", 0.92)),
    )
    material(
        configuration,
        "epoxy",
        "epoxy glue 1.16 g/cm3",
        1.16,
        atoms=(("H", 32), ("N", 2), ("O", 4), ("C", 15)),
    )
    material(
        configuration,
        "carbonFiber",
        "ft carbon fiber material is epoxy and carbon - 1.75g/cm3",
        1.75,
        fractions=(("G4_C", 0.745), ("epoxy", 0.255)),
    )
    material(
        configuration,
        "pcboard",
        "ft pcb 1.86 g/cm3",
        1.86,
        fractions=(("G4_Fe", 0.3), ("G4_C", 0.4), ("G4_Si", 0.3)),
    )
    material(
        configuration,
        "insfoam",
        "ft insulation foam 34 kg/m3",
        0.034,
        fractions=(("G4_C", 0.6), ("G4_H", 0.1), ("G4_N", 0.1), ("G4_O", 0.2)),
    )
    material(
        configuration,
        "scintillator",
        "ft scintillator material C9H10 1.032 g/cm3",
        1.032,
        atoms=(("C", 9), ("H", 10)),
    )
    material(
        configuration,
        "myFR4",
        "pcb FR4",
        1.86,
        fractions=(("G4_C", 0.4355), ("G4_H", 0.0365), ("G4_Si", 0.2468), ("G4_O", 0.2812)),
    )
    material(configuration, "mmstrips", "ft micromegas strips", "9.19642218246869",
             fractions=(("G4_Cu", 1),))
    material(configuration, "ResistPaste", "micromegas fmt resistiv strips", "1.0773",
             fractions=(("G4_C", 1),))
    material(
        configuration,
        "mmmesh",
        "ft micromegas mesh",
        7.93 * 0.55,
        fractions=(
            ("G4_Mn", 0.02),
            ("G4_Si", 0.01),
            ("G4_Cr", 0.19),
            ("G4_Ni", 0.10),
            ("G4_Fe", 0.68),
        ),
    )
    material(
        configuration,
        "mmgas",
        "ft micromegas gas",
        "0.00170335",
        fractions=(("G4_Ar", 0.95), ("G4_H", 0.0086707), ("G4_C", 0.0413293)),
    )
    material(configuration, "myPhRes", "PhotoResist", 1.42, fractions=(("G4_C", 1),))
    material(
        configuration,
        "mmmylar",
        "ft micromegas mylar 1.40g/cm3",
        1.4,
        fractions=(("G4_H", 0.041958), ("G4_C", 0.625017), ("G4_O", 0.333025)),
    )
