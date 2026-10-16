"""Passive beamline geometry translated from the current clas12Tags Perl builders.

Only volumes published by beamline.pl are built here. The disabled HD-ice daughters
in rghline.pl and the older, uncalled torus/tungsten builders remain disabled.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

from pygemc import GVolume

from beamline_parameters import (
    DOWNSTREAM_PLANES, DOWNSTREAM_RADII, MEDIUM_START, PIPE_FIRST_STEP,
    SHORT_PIPE_VARIATIONS, TORUS_START,
)


def _volume(name, description, material, color, z=0, mother="root"):
    volume = GVolume(name)
    volume.mother = mother
    volume.description = description
    volume.material = material
    volume.color = color
    volume.style = 1
    volume.position = f"0*mm, 0*mm, {z:.15g}*mm"
    return volume


def _tube(cfg, name, radius, length, z=0, inner=0, mother="root",
          material="G4_STAINLESS-STEEL", color="aaffff", description="straightVacuumPipe"):
    volume = _volume(name, description, material, color, z, mother)
    volume.make_tube(inner, radius, length, 0, 360)
    volume.publish_passive(cfg)


def _polycone(cfg, name, planes, inner, outer, material, color, description, z=0):
    volume = _volume(name, description, material, color, z)
    volume.make_polycone(zplane=planes, iradius=inner, oradius=outer)
    volume.publish_passive(cfg)


def _pipe_pair(cfg, number, start, end, inner, outer, description="straightVacuumPipe"):
    length = (end - start) / 2 - 0.1
    _tube(cfg, f"vacuumPipe{number}", outer, length, start + length, description=description)
    _tube(cfg, f"vacuumInPipe{number}", inner, length, mother=f"vacuumPipe{number}",
          material="G4_Galactic", color="000000")


def _downstream(cfg, end):
    _polycone(cfg, "beam_vacuum", (*DOWNSTREAM_PLANES, end), (0,) * 7, DOWNSTREAM_RADII,
              "G4_Galactic", "000000", "vacuum line inside torus")


def _window(cfg, z, radius):
    # Preserve the GEMC2 description, including its historical thickness typo.
    _tube(cfg, "al_window_vacuum_entrance", radius, 0.0375, z, material="G4_Al", color="aaaaff",
          description="50 mm thick aluminum window downstream")


def _vacuum_line(cfg):
    variation = cfg.variation
    short = variation in SHORT_PIPE_VARIATIONS
    ddvcs = variation == "ddvcs"
    start = 503 if short else 963
    first_inner, first_outer = (22.924, 24.52) if ddvcs else (26.924, 28.52)
    second_inner, second_outer = (24.275, 32.925) if ddvcs else (33.275, 34.925)
    connecting_inner = second_inner + (3.1 if ddvcs else 0.1)

    _pipe_pair(cfg, 1, start, PIPE_FIRST_STEP, first_inner, first_outer)
    _pipe_pair(cfg, 2, MEDIUM_START, TORUS_START, second_inner, second_outer)
    length = (MEDIUM_START - PIPE_FIRST_STEP) / 2 - 0.1
    z = PIPE_FIRST_STEP + length
    _tube(cfg, "vacuumPipe3", second_outer, length, z, inner=connecting_inner)
    _tube(cfg, "vacuumInPipe3", first_outer, length, z, material="G4_Galactic", color="000000")
    _window(cfg, 502.5 if short else 962.5, 24.52 if ddvcs else 30)
    _downstream(cfg, 10000)

    if not ddvcs:
        gap_length = 86.5 if short else 295
        description = "airgap between target and shield to limit e- steps"
        _polycone(cfg, "airPipe", (0, 2 * gap_length), (0, 0), (20, 30),
                  "G4_AIR", "aaffff", description, z=283)
        _tube(cfg, "airPipe2", 10, gap_length - 0.2, gap_length - 0.2, mother="airPipe",
              material="G4_AIR", description=description)


def _elmo_line(cfg):
    _pipe_pair(cfg, 1, 787.41, PIPE_FIRST_STEP, 33.275, 34.925,
               description="straightVacuumPipe 2.75 inch OD 0.065 thick ")
    _pipe_pair(cfg, 2, MEDIUM_START, TORUS_START, 33.275, 34.925)
    length = (MEDIUM_START - PIPE_FIRST_STEP) / 2 - 0.1
    z = PIPE_FIRST_STEP + length
    # ELMOline.pl uses 33.275 here, rather than its unused connectingIR = 33.375.
    _tube(cfg, "vacuumPipe3", 34.925, length, z, inner=33.275)
    _tube(cfg, "vacuumInPipe3", 33.275, length, z, material="G4_Galactic", color="000000")
    _downstream(cfg, 13900)

    planes = (716.42, 1249.40, 1249.40, 1351.00)
    middle_radius = 53.28 + (105.78 - 53.28) * (planes[1] - planes[0]) / (planes[3] - planes[0])
    _polycone(cfg, "ElmoTungstenCone", planes, (38.10, 38.10, 47.62, 47.62),
              (53.28, middle_radius, middle_radius, 105.78), "beamline_W", "dd8648",
              "Tungsten moller shield - ELMO configuration")
    _polycone(cfg, "ElmoTungstenTip", (570, planes[0]), (39, 38.10), (41.2, 53.28),
              "beamline_W", "dd8648", "Tungsten Tip - ELMO configuration")
    for index, lead_planes in enumerate(((1357.35, 1802.71), (1809.06, 2240.86)), start=1):
        _polycone(cfg, f"ElmoPbCylinder{index}", lead_planes, (47.62,) * 2, (105.78,) * 2,
                  "G4_Pb", "999966", f"Lead Cylinder {index} - ELMO configuration")
    _polycone(cfg, "ElmoSteelCase", (1357.35 - 5, 2240.86 + 15), (105.78,) * 2, (109.54,) * 2,
              "G4_STAINLESS-STEEL", "666666", "Steel Case - ELMO configuration")
    _polycone(cfg, "ElmoSupportPipe", (1249.40, 2240.86, 2240.86, 2240.86 + 27.5),
              (38.10,) * 4, (47.62, 47.62, 105.78, 105.78), "G4_STAINLESS-STEEL", "669966",
              "Steel support pipe - ELMO configuration")
    _polycone(cfg, "ElmoAirPipe", (54, 385, 385, 570), (0,) * 4, (10, 10, 25.46, 41.2),
              "G4_AIR", "aaffff", "Air pipe - ELMO configuration")


def _cons(cfg, name, z, inner1, outer1, inner2, outer2, length, material, color, description):
    volume = _volume(name, description, material, color, z)
    volume.make_cons(inner1, outer1, inner2, outer2, length, 0, 360)
    volume.publish_passive(cfg)


def _rgh_line(cfg):
    _tube(cfg, "vacuumPipe1_2", 34.925, 728.4, 1528.4,
          description="straightVacuumPipe 2.75 inch OD 0.065 thick ")
    _tube(cfg, "vacuumInPipe1_2", 33.325, 728.4, mother="vacuumPipe1_2",
          material="G4_Galactic", color="000000")
    _tube(cfg, "vacuumPipe2", 34.925, 132.235, 2621.735)
    _tube(cfg, "vacuumInPipe2", 33.275, 132.235, mother="vacuumPipe2",
          material="G4_Galactic", color="000000")
    _tube(cfg, "vacuumPipe3", 34.925, 38.15, 2451.15, inner=33.375)
    _tube(cfg, "vacuumInPipe3", 33.375, 38.15, 2451.15, material="G4_Galactic", color="000000")
    _downstream(cfg, 13900)

    _cons(cfg, "Cone1_2", 1013.25, 38.1, 61.3313, 38.1, 98.64, 213.25,
          "beamline_W", "dd8648", "AngelaBrenna Tungsten Tip")
    _cons(cfg, "Cone2", 1290.05, 47.62, 98.64, 47.62, 109.76, 63.55,
          "beamline_W", "dd8648", "AngelaBrenna Tungsten Tip")

    ft_out = cfg.variation == "rghFTOut"
    _cons(cfg, "Cylinder", 1797.755 if ft_out else 1556.8, 47.63, 109.76, 47.63, 109.76,
          444.155 if ft_out else 203.2, "G4_Pb", "c57742",
          "Moller Shield Pb pipe on beamline, NW80 flange is 2.87 inch inner diameter")
    _cons(cfg, "SupportTube", 1743.2 if ft_out else 1493.25, 38.1, 47.6, 38.1, 47.6,
          516.7 if ft_out else 266.75, "G4_Pb", "ac6839", "2nd Moller Shield Cone outside beam pipe  ")
    if ft_out:
        _cons(cfg, "FTPreShieldCylinder", 2018.765, 35, 108.5, 35, 108.5, 241.135,
              "G4_Pb", "945931", "Shield before FT on beamline")
    _cons(cfg, "FTflangeShieldCylinder", 2300 if ft_out else 2305.45,
          125.4, 130, 125.4, 130, 41.3 if ft_out else 35.85,
          "G4_Pb", "999966", "Shield around beam puipe flange")
    _cons(cfg, "TorusConnector", 2550, 97, 104, 97, 104, 101.3,
          "G4_Pb", "999966", "Shield around Shield support before FT on beamline")


def _elmo7(cfg):
    _polycone(cfg, "elmo7", (250, 360, 570, 1750, 1750, 2280, 2380, 2750),
              (21, 21, 26.1, 26.1, 26.1, 33.1, 33.1, 33.1),
              (29, 29, 41.2, 126.5, 218, 218, 111, 111), "beamline_W", "dd8648",
              "Tungsten Cone - elmo7 configuration")
    planes = (570, 2280, 2280, 2380, 2750)
    inner = (22, 22, 28, 28, 28)
    outer = (24, 24, 32.9, 32.9, 32.9)
    _polycone(cfg, "vacuumPipe1", planes, (0,) * 5, outer,
              "G4_STAINLESS-STEEL", "aaffff", "straightVacuumPipe")
    volume = _volume("vacuumInPipe1", "straightVacuumPipe", "G4_Galactic", "000000",
                     mother="vacuumPipe1")
    volume.make_polycone(zplane=planes, iradius=(0,) * 5, oradius=inner)
    volume.publish_passive(cfg)
    _window(cfg, planes[0] - 0.0375, outer[0])
    _downstream(cfg, 10000)


def build_beamline(configuration):
    variation = configuration.variation
    if variation == "rgc_fall2022":
        _elmo_line(configuration)
    elif variation == "TransverseUpstreamBeampipe":
        for index, length, z in ((1, 500, -858), (2, 148, -204)):
            name = f"upstreamTransverseMagnetVacuumPipe{index}"
            _tube(configuration, name, 35, length, z, material="G4_Galactic", color="334488",
                  description=name)
    elif variation in ("rghFTOut", "rghFTOn"):
        _rgh_line(configuration)
    elif variation == "elmo7":
        _elmo7(configuration)
    else:
        if variation == "ddvcs":
            _polycone(configuration, "ddvcs_mollercone", (300, 1251, 2280, 2380, 2750),
                      (26.1, 26.1, 33.1, 33.1, 33.1), (30.6, 149, 149, 111, 111),
                      "beamline_W", "222288", "Moller Cone")
        _vacuum_line(configuration)


def build_cad(configuration, transverse=False):
    """Publish the original GXML placements with millimetre, unscaled STL paths."""
    directory = Path(__file__).resolve().parent
    if transverse:
        variant = configuration.variation
        placements = directory / "cad_transverse" / variant / "cad_default.gxml"
        mesh_directory = f"stls/{variant}"
    else:
        placements = directory / "cad" / f"cad_{configuration.variation}.gxml"
        mesh_directory = "stls"
    for row in ET.parse(placements).getroot().findall("volume"):
        name = row.attrib["name"]
        volume = GVolume(name)
        volume.mother = row.get("mother", "root")
        volume.material = row.attrib["material"]
        volume.color = row.attrib["color"]
        volume.position = ", ".join(row.get("position", "0*mm 0*mm 0*mm").split())
        volume.rotations = [", ".join(row.get("rotation", "0*deg 0*deg 0*deg").split())]
        volume.style = 1
        volume.solid = "CAD"
        volume.parameters = f"{mesh_directory}/{name}.stl, 1"
        volume.publish_passive(configuration)
