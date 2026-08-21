"""CLAS12 Forward Tagger geometry, ported from clas12Tags ``geometry_source/ft``.

The Forward Tagger consists of the PbWO4 calorimeter (FTCAL), scintillator hodoscope
(FTHODO), and two-disk Micromegas tracker (FTTRK). Values are kept in millimetres and
formatted with Perl's default numeric precision so the generated ASCII database can be
compared directly with the GEMC2 reference.
"""

import math

from pygemc import GVolume


TRACKER_ABSENT = {
    "rgk_winter2018",
    "rgf_spring2020",
    "rgc_summer2022",
    "rgd_fall2023",
}


def fstr(value):
    """Format a number like Perl's default stringification (``%.15g``)."""
    formatted = f"{float(value):.15g}"
    return "0" if formatted == "-0" else formatted


def build_ft(configuration):
    """Publish FTCAL, FTHODO, and the variation-dependent FTTRK."""
    build_calorimeter(configuration)
    build_hodoscope(configuration)
    if configuration.variation not in TRACKER_ABSENT:
        build_tracker(configuration)


# ---------------------------------------------------------------------------
# FTCAL
# ---------------------------------------------------------------------------

CWIDTH = 15.0
CLENGTH = 200.0
FLENGTH = 8.0
VWIDTH = CWIDTH + 0.130 + 0.170
V_LENGTH = CLENGTH + FLENGTH
V_FRONT = 1897.8 - FLENGTH
S_LENGTH = 7.0
S_FRONT = V_FRONT + V_LENGTH + 1.0

B_DISK_TN = 4.0
B_DISK_IR = 55.0
B_DISK_OR = 178.5
B_DISK_Z = S_FRONT + S_LENGTH + B_DISK_TN + 0.1
F_DISK_TN = 1.0
F_DISK_Z = V_FRONT - F_DISK_TN - 0.1
B_PLATE_TN = 25.0
B_PLATE_Z = B_DISK_Z + B_DISK_TN + B_PLATE_TN + 0.1
I_DISK_LT = (B_PLATE_Z + B_PLATE_TN - F_DISK_Z + F_DISK_TN) / 2.0
I_DISK_OR = B_DISK_IR
I_DISK_IR = I_DISK_OR - 4.0
I_DISK_Z = (B_PLATE_Z + B_PLATE_TN + F_DISK_Z - F_DISK_TN) / 2.0
O_DISK_IR = B_DISK_OR
O_DISK_OR = O_DISK_IR + 2.0
O_DISK_Z = I_DISK_Z

B_MTB_TN = 1.0
B_MTB_IR = I_DISK_IR
B_MTB_OR = O_DISK_OR
B_MTB_Z = B_PLATE_Z + B_PLATE_TN + B_MTB_TN + 0.1
B_MTB_HEAR_WD = 40.0
B_MTB_HEAR_LN = 112.5
B_MTB_ANGLES = (30.0, 150.0, 210.0, 330.0)

LED_TN = 6.1
LED_Z = F_DISK_Z - F_DISK_TN - LED_TN - 0.1
B_LINE_IR = 30.0
B_LINE_TN = 10.0
B_LINE_OR = 100.0
B_LINE_BG = 1644.7
B_LINE_ML = 1760.0
B_LINE_MR = B_LINE_IR + B_LINE_TN

B_CUP_TANG = 0.0962
B_CUP_TN = 5.0
B_CUP_ZM = B_MTB_Z + B_MTB_TN + 0.1 + 43.4
B_CUP_Z1 = B_MTB_Z + B_MTB_TN + 0.1 + 1.0
B_CUP_Z2 = B_MTB_Z - B_MTB_TN - 0.1 - 1.0
B_CUP_ZE = B_CUP_ZM + B_CUP_TN
B_CUP_ZB = B_CUP_ZM - 120.0
B_CUP_IRM = 190.0
B_CUP_ORB = B_CUP_ZB * B_CUP_TANG
B_CUP_OR1 = B_CUP_Z1 * B_CUP_TANG
B_CUP_OR2 = B_CUP_Z2 * B_CUP_TANG
B_CUP_ORM = B_CUP_ZM * B_CUP_TANG
B_CUP_ORE = B_CUP_ZE * B_CUP_TANG
B_CUP_ANGLE = int(math.atan(B_MTB_HEAR_WD / B_MTB_OR) * 57.27 * 10) / 10 + 0.5
B_CUP_IANGLES = tuple(angle + B_CUP_ANGLE for angle in B_MTB_ANGLES)
B_CUP_DANGLES = (
    (90.0 - B_CUP_IANGLES[0]) * 2.0,
    (180.0 - B_CUP_IANGLES[1]) * 2.0,
    (90.0 - B_CUP_IANGLES[0]) * 2.0,
    (180.0 - B_CUP_IANGLES[1]) * 2.0,
)

T_PLATE_TN = 20.0
O_INS_TN = 15.0 - 0.01
O_INS_Z = [
    F_DISK_Z - F_DISK_TN - LED_TN * 2 - 10.8 - O_INS_TN,
]
O_INS_Z += [O_INS_Z[0] + O_INS_TN, B_CUP_ZB, B_CUP_Z2, B_CUP_Z1, B_CUP_ZM, B_CUP_ZE]
O_INS_Z += [B_CUP_ZE + 0.01]
O_INS_Z += [O_INS_Z[7] + O_INS_TN, O_INS_Z[7] + O_INS_TN]
O_INS_Z += [O_INS_Z[9] + T_PLATE_TN]
O_INS_I = [
    B_LINE_IR + B_LINE_TN + 0.01,
    O_INS_Z[1] * B_CUP_TANG + 0.01,
    O_INS_Z[2] * B_CUP_TANG + 0.01,
    O_INS_Z[3] * B_CUP_TANG + 0.5,
    O_INS_Z[4] * B_CUP_TANG + 0.5,
    O_INS_Z[5] * B_CUP_TANG + 0.01,
    O_INS_Z[6] * B_CUP_TANG + 0.01,
    O_INS_Z[7] * B_CUP_TANG + 0.01,
    B_LINE_IR + B_LINE_TN + 0.01,
    O_INS_Z[9] * B_CUP_TANG + 0.01,
    O_INS_Z[9] * B_CUP_TANG + 0.01,
]
O_INS_O = [O_INS_Z[0] * B_CUP_TANG + 0.01 + O_INS_TN]
O_INS_O += [O_INS_Z[index] * B_CUP_TANG + 0.01 + O_INS_TN for index in range(1, 8)]
O_INS_O += [O_INS_Z[8] * B_CUP_TANG + 0.01 + O_INS_TN]
O_INS_O += [O_INS_I[9] + O_INS_TN, O_INS_I[10] + O_INS_TN]

I_INS_LT = (B_CUP_ZE - O_INS_Z[1] - 0.1) / 2.0
I_INS_OR = I_DISK_IR - 0.1
I_INS_IR = O_INS_I[0]
I_INS_Z = (B_CUP_ZE + O_INS_Z[1]) / 2.0

O_SHELL_TN = 2.0 - 0.01
O_SHELL_Z = [O_INS_Z[0] - O_SHELL_TN - 0.01]
O_SHELL_Z += [O_SHELL_Z[0] + O_SHELL_TN, O_INS_Z[2], B_CUP_Z2, B_CUP_Z1]
O_SHELL_Z += O_INS_Z[5:10]
O_SHELL_Z += [O_INS_Z[10] + 0.01, O_INS_Z[10] + 0.01]
O_SHELL_Z += [O_SHELL_Z[11] + O_SHELL_TN]
O_SHELL_I = [O_INS_I[0]]
O_SHELL_I += [z * B_CUP_TANG + O_INS_TN + 0.01 for z in O_SHELL_Z[1:11]]
O_SHELL_I += [O_SHELL_I[10] - O_INS_TN - 5.0, O_SHELL_I[10] - O_INS_TN - 5.0]
O_SHELL_O = [O_SHELL_Z[0] * B_CUP_TANG + O_INS_TN + 0.01 + O_SHELL_TN]
O_SHELL_O += [value + O_SHELL_TN for value in O_SHELL_I[1:11]]
O_SHELL_O += [O_SHELL_O[10], O_SHELL_O[10]]
O_SHELL_I[3] = O_SHELL_Z[3] * B_CUP_TANG + O_INS_TN + 0.7
O_SHELL_I[4] = O_SHELL_Z[4] * B_CUP_TANG + O_INS_TN + 0.7

T_PLATE_RR = T_PLATE_TN * 0.6
T_PLATE_Z1 = O_INS_Z[8] + 0.01
T_PLATE_Z2 = T_PLATE_Z1 + T_PLATE_TN - 0.01
T_PLATE_ZM = T_PLATE_Z2 - T_PLATE_RR
T_PLATE_MR = B_LINE_IR + B_LINE_TN + T_PLATE_RR
B_LINE_Z2 = B_LINE_ML + 0.2
B_LINE_Z4 = T_PLATE_Z2 + 0.01
B_LINE_Z5 = B_LINE_Z4 - 0.01 + 20.0


def build_calorimeter(configuration):
    """Build the FTCAL crystals, supports, insulation, shell, and beamline pieces."""
    volume = GVolume("ft_cal", value_formatter=fstr)
    volume.description = "ft calorimeter"
    volume.color = "1437f4"
    volume.make_polycone(
        zplane=(O_SHELL_Z[0], 2098.0, T_PLATE_ZM, B_LINE_Z4, B_LINE_Z4, B_LINE_Z5),
        iradius=(B_LINE_MR, B_LINE_MR, B_LINE_MR, T_PLATE_MR, B_LINE_OR, B_LINE_OR),
        oradius=(700.0, 700.0, 238.0, 238.0, 238.0, 238.0),
    )
    volume.material = "G4_AIR"
    volume.visible = 0
    volume.publish_passive(configuration)
    volume = GVolume("ft_calCrystalsMother", value_formatter=fstr)
    volume.description = "ft calorimeter crystal volume"
    volume.mother = "ft_cal"
    volume.color = "1437f4"
    volume.make_polycone(
        zplane=(I_DISK_Z - I_DISK_LT, I_DISK_Z + I_DISK_LT),
        iradius=(I_DISK_IR,) * 2,
        oradius=(O_DISK_OR,) * 2,
    )
    volume.material = "G4_AIR"
    volume.style = 0
    volume.publish_passive(configuration)
    build_crystals(configuration)
    build_calorimeter_flux(configuration)
    build_calorimeter_copper(configuration)
    build_calorimeter_motherboard(configuration)
    build_calorimeter_shielding(configuration)


def build_crystals(configuration):
    """Build the 332 crystal assemblies accepted by the radial cut."""
    center = 11.5
    for ix in range(1, 23):
        for iy in range(1, 23):
            x = (ix - center) * VWIDTH
            y = (iy - center) * VWIDTH
            radius = math.hypot(x, y)
            if not 60.0 < radius < VWIDTH * 11:
                continue

            suffix = f"h{ix}_v{iy}"
            mother_name = f"ft_cal_cr_motherVolume_{suffix}"
            wrap_name = f"ft_cal_cr_wrap_{suffix}"
            volume = GVolume(mother_name, value_formatter=fstr)
            volume.description = f"Mother Volume for crystal h:{ix}, v:{iy}"
            volume.mother = "ft_calCrystalsMother"
            volume.set_position(x, y, V_FRONT + V_LENGTH / 2)
            volume.color = "838EDE"
            volume.make_box(VWIDTH / 2, VWIDTH / 2, V_LENGTH / 2)
            volume.material = "G4_AIR"
            volume.style = 0
            volume.publish_passive(configuration)
            volume = GVolume(f"ft_cal_cr_apd_{suffix}", value_formatter=fstr)
            volume.description = f"apd for crystal h:{ix}, v:{iy}"
            volume.mother = "ft_calCrystalsMother"
            volume.set_position(x, y, S_FRONT + S_LENGTH / 2)
            volume.color = "99CC66"
            volume.make_box(CWIDTH / 2, CWIDTH / 2, S_LENGTH / 2)
            volume.material = "ft_peek"
            volume.publish_passive(configuration)
            volume = GVolume(wrap_name, value_formatter=fstr)
            volume.description = f"wrapping for crystal h:{ix}, v:{iy}"
            volume.mother = mother_name
            volume.color = "838EDE"
            volume.make_box((CWIDTH + 0.130) / 2, (CWIDTH + 0.130) / 2, V_LENGTH / 2)
            volume.material = "G4_MYLAR"
            volume.publish_passive(configuration)
            volume = GVolume(f"ft_cal_cr_{suffix}", value_formatter=fstr)
            volume.description = f"PbWO4 crystal h:{ix}, v:{iy}"
            volume.mother = wrap_name
            volume.set_position(0, 0, FLENGTH / 2)
            volume.color = "836FFF"
            volume.make_box(CWIDTH / 2, CWIDTH / 2, CLENGTH / 2)
            volume.material = "G4_PbWO4"
            volume.digitization = "ft_cal"
            volume.set_identifier(*("ih", ix, "iv", iy))
            volume.publish_passive(configuration)
            volume = GVolume(f"ft_cal_cr_ledHousing_{suffix}", value_formatter=fstr)
            volume.description = f"Led Housing for crystal h:{ix}, v:{iy}"
            volume.mother = wrap_name
            volume.set_position(0, 0, -V_LENGTH / 2 + FLENGTH / 2)
            volume.color = "EEC900"
            volume.make_box(CWIDTH / 2, CWIDTH / 2, FLENGTH / 2)
            volume.material = "ft_peek"
            volume.publish_passive(configuration)


def build_calorimeter_flux(configuration):
    """Build the crystal-back and upstream flux planes."""
    volume = GVolume("ft_cal_flux", value_formatter=fstr)
    volume.description = "ft flux"
    volume.mother = "ft_calCrystalsMother"
    volume.set_position(0, 0, V_FRONT + V_LENGTH + 0.5)
    volume.color = "aa0088"
    volume.make_tube(B_DISK_IR, B_DISK_OR, 0.5)
    volume.material = "G4_Galactic"
    volume.digitization = "flux"
    volume.set_identifier(*("id", 3))
    volume.publish_passive(configuration)
    volume = GVolume("moller_disk_1", value_formatter=fstr)
    volume.description = "Moller Disk 1"
    volume.set_position(0, 0, O_SHELL_Z[0] - 0.05)
    volume.color = "aa0088"
    volume.make_tube(56.0, 150.0, 0.05)
    volume.material = "G4_Galactic"
    volume.visible = 0
    volume.digitization = "flux"
    volume.set_identifier(*("id", 2))
    volume.publish_passive(configuration)


def build_calorimeter_copper(configuration):
    """Build the copper thermal envelope and preamp air volume."""
    pieces = (
        ("back_copper", "back_copper", B_DISK_Z, B_DISK_IR, B_DISK_OR, B_DISK_TN, "G4_Cu", "CC6600"),
        ("front_copper", "front_copper", F_DISK_Z, B_DISK_IR, B_DISK_OR, F_DISK_TN, "G4_Cu", "CC6600"),
        ("inner_copper", "inner_copper", I_DISK_Z, I_DISK_IR, I_DISK_OR, I_DISK_LT, "G4_Cu", "CC6600"),
        ("outer_copper", "outer_copper", O_DISK_Z, O_DISK_IR, O_DISK_OR, I_DISK_LT, "G4_Cu", "CC6600"),
        ("back_plate", "back_plate", B_PLATE_Z, B_DISK_IR, B_DISK_OR, B_PLATE_TN, "G4_AIR", "7F9A65"),
    )
    for name, description, z, inner, outer, half_length, material, color in pieces:
        volume = GVolume(f"ft_cal_{name}", value_formatter=fstr)
        volume.description = f"ft {description}"
        volume.mother = "ft_calCrystalsMother"
        volume.set_position(0, 0, z)
        volume.color = color
        volume.make_tube(inner, outer, half_length)
        volume.material = material
        volume.publish_passive(configuration)


def build_calorimeter_motherboard(configuration):
    """Build the rear motherboard disk, ears, and LED plate."""
    volume = GVolume("ft_cal_back_mtb", value_formatter=fstr)
    volume.description = "ft back_mtb disk"
    volume.mother = "ft_cal"
    volume.set_position(0, 0, B_MTB_Z)
    volume.color = "0B3B0B"
    volume.make_tube(B_MTB_IR, B_MTB_OR, B_MTB_TN)
    volume.material = "pcboard"
    volume.publish_passive(configuration)
    for index, angle in enumerate(B_MTB_ANGLES):
        radians = angle / 57.27
        distance = B_MTB_OR + B_MTB_HEAR_LN
        volume = GVolume(f"ft_cal_back_mtb_h{index}", value_formatter=fstr)
        volume.description = f"ft back_mtb hear{index}"
        volume.mother = "ft_cal"
        volume.set_position(distance * math.cos(radians), -distance * math.sin(radians), B_MTB_Z)
        volume.rotations = [f'0*deg, 0*deg, {fstr(angle)}*deg']
        volume.color = "0B3B0B"
        volume.make_box(B_MTB_HEAR_LN, B_MTB_HEAR_WD, B_MTB_TN)
        volume.material = "pcboard"
        volume.publish_passive(configuration)
    volume = GVolume("ft_cal_led", value_formatter=fstr)
    volume.description = "ft led"
    volume.mother = "ft_cal"
    volume.set_position(0, 0, LED_Z)
    volume.color = "333333"
    volume.make_tube(B_DISK_IR, B_DISK_OR, LED_TN)
    volume.material = "ft_peek"
    volume.publish_passive(configuration)


def build_calorimeter_shielding(configuration):
    """Build the tungsten cup, insulation, shell, and active beamline pieces."""
    cup_parts = (
        ("ft_cal_tcup_back", "tungsten cup and cone at the back of the ft, back part",
         (B_CUP_IRM,) * 2, (B_CUP_OR1, B_CUP_ORM), (B_CUP_Z1, B_CUP_ZM), "ft_W", "ff0000"),
        ("ft_cal_tcup_plate", "stainless steel plate at the back of the ft", (I_INS_OR,) * 2,
         (B_CUP_ORM, B_CUP_ORE), (B_CUP_ZM, B_CUP_ZE), "G4_STAINLESS-STEEL", "cccccc"),
        ("ft_cal_tcup_front", "tungsten cup and cone at the back of the ft, front part",
         (B_CUP_IRM,) * 2, (B_CUP_ORB, B_CUP_OR2), (B_CUP_ZB, B_CUP_Z2), "ft_W", "ff0000"),
    )
    for name, description, inner, outer, z, material, color in cup_parts:
        volume = GVolume(name, value_formatter=fstr)
        volume.description = description
        volume.mother = "ft_cal"
        volume.color = color
        volume.make_polycone(zplane=z, iradius=inner, oradius=outer)
        volume.material = material
        volume.publish_passive(configuration)
    for index, (start, delta) in enumerate(zip(B_CUP_IANGLES, B_CUP_DANGLES), start=1):
        volume = GVolume(f"ft_cal_tcup_m{index}", value_formatter=fstr)
        volume.description = f"tungsten cup and cone at the back of the ft, medium part {index}"
        volume.mother = "ft_cal"
        volume.color = "ff0000"
        volume.make_polycone(
            start,
            delta,
            (B_CUP_Z1, B_CUP_Z2),
            (B_CUP_IRM,) * 2,
            (B_CUP_OR1, B_CUP_OR2),
        )
        volume.material = "ft_W"
        volume.publish_passive(configuration)

    volume = GVolume("ft_cal_inner_ins", value_formatter=fstr)
    volume.description = "ft inner_ins"
    volume.mother = "ft_cal"
    volume.set_position(0, 0, I_INS_Z)
    volume.color = "F5F6CE"
    volume.make_tube(I_INS_IR, I_INS_OR, I_INS_LT)
    volume.material = "insfoam"
    volume.publish_passive(configuration)
    build_segmented_polycones(configuration, "ins", "F5F6CE", "insfoam", O_INS_Z, O_INS_I, O_INS_O)
    build_segmented_polycones(
        configuration,
        "shell",
        "F5DA81",
        "carbonFiber",
        O_SHELL_Z,
        O_SHELL_I,
        O_SHELL_O,
    )

    tplate_inner = (B_LINE_MR, B_LINE_MR, T_PLATE_MR)
    tplate_outer = (T_PLATE_Z1 * B_CUP_TANG,) * 3
    volume = GVolume("ft_cal_tplate", value_formatter=fstr)
    volume.description = "ft tungsten plate"
    volume.mother = "ft_cal"
    volume.color = "ff0000"
    volume.make_polycone(
        zplane=(T_PLATE_Z1, T_PLATE_ZM, T_PLATE_Z2),
        iradius=tplate_inner,
        oradius=tplate_outer,
    )
    volume.material = "ft_W"
    volume.publish_passive(configuration)


def build_segmented_polycones(configuration, kind, color, material, z, inner, outer):
    """Build the front, rear, and four azimuthal middle insulation/shell pieces."""
    if kind == "ins":
        prefix = "ft_cal_outer_ins"
        description = "ft outer_ins"
        back_inner_indices = (4, 5, 6, 7, 8, 8, 9, 10)
        back_outer_indices = (4, 5, 6, 7, 7, 8, 9, 10)
        back_z_indices = back_outer_indices
    else:
        prefix = "ft_cal_outer_shell"
        description = "ft outer_shell"
        back_inner_indices = tuple(range(4, 13))
        back_outer_indices = back_inner_indices
        back_z_indices = back_inner_indices

    volume = GVolume(f"{prefix}_f", value_formatter=fstr)
    volume.description = f"{description}_f"
    volume.mother = "ft_cal"
    volume.color = color
    volume.make_polycone(
        zplane=tuple(z[index] for index in (0, 1, 1, 2, 3)),
        iradius=tuple(inner[index] for index in (0, 0, 1, 2, 3)),
        oradius=tuple(outer[index] for index in (0, 1, 1, 2, 3)),
    )
    volume.material = material
    volume.publish_passive(configuration)
    volume = GVolume(f"{prefix}_b", value_formatter=fstr)
    volume.description = f"{description}_b"
    volume.mother = "ft_cal"
    volume.color = color
    volume.make_polycone(
        zplane=tuple(z[index] for index in back_z_indices),
        iradius=tuple(inner[index] for index in back_inner_indices),
        oradius=tuple(outer[index] for index in back_outer_indices),
    )
    volume.material = material
    volume.publish_passive(configuration)
    for index, (start, delta) in enumerate(zip(B_CUP_IANGLES, B_CUP_DANGLES), start=1):
        middle_description = f"{description}_m{index}" if kind == "ins" else f"{description} {index}"
        volume = GVolume(f"{prefix}_m{index}", value_formatter=fstr)
        volume.description = middle_description
        volume.mother = "ft_cal"
        volume.color = color
        volume.make_polycone(
            start,
            delta,
            (z[4], z[3]),
            (inner[4], inner[3]),
            (outer[4], outer[3]),
        )
        volume.material = material
        volume.publish_passive(configuration)


# ---------------------------------------------------------------------------
# FTHODO
# ---------------------------------------------------------------------------

VETO_TN = 19.0
VETO_OR = 178.5
VETO_IR = 40.0
VETO_Z = O_SHELL_Z[0] - VETO_TN - 0.1
VETO_RING_TN = 18.5
VETO_RING_OR = 52.5
VETO_RING_Z = O_SHELL_Z[0] - VETO_RING_TN - 0.1
PAINT_TN = 0.1
TILE_WIDTH = 15.0
S1_X = (3.25, 2.5, 4.25, 3.5, 2.5, 4.5, 3.5, 2.5, 1.75)
S1_Y = (4.25, 4.5, 3.25, 3.5, 3.5, 2.5, 2.5, 2.5, 1.75)
S1_W = (1.0, 2.0, 1.0, 2.0, 2.0, 2.0, 2.0, 2.0, 1.0)
S2_X = (1.5, 0.5, -0.5, -1.5, 1.5, 0.5, -0.5, -1.5, 1.5, 0.5, -0.5, -1.5,
        1.75, 1.25, 0.75, 0.25, -0.25, -0.75, -1.25, -1.75)
S2_Y = (5.0,) * 4 + (4.0,) * 4 + (3.0,) * 4 + (2.25,) * 8
S2_W = (2.0,) * 12 + (1.0,) * 8


def build_hodoscope(configuration):
    """Build the two scintillator layers and their carbon-fibre support."""
    volume = GVolume("ft_hodo", value_formatter=fstr)
    volume.description = "ft scintillation hodoscope"
    volume.color = "3399FF"
    volume.make_polycone(
        zplane=(VETO_Z - VETO_TN, 1810.6, 1810.6, VETO_Z + VETO_TN),
        iradius=(VETO_RING_OR, VETO_RING_OR, VETO_IR, VETO_IR),
        oradius=(VETO_OR,) * 4,
    )
    volume.material = "G4_AIR"
    volume.visible = 0
    volume.publish_passive(configuration)
    volume = GVolume("ft_hodo_innervol", value_formatter=fstr)
    volume.description = "ft scintillation hodoscope inner volume"
    volume.mother = "ft_hodo"
    volume.set_position(0, 0, VETO_Z)
    volume.color = "3399FF"
    volume.make_tube(VETO_RING_OR, VETO_OR, VETO_TN)
    volume.material = "G4_AIR"
    volume.visible = 0
    volume.publish_passive(configuration)
    volume = GVolume("ft_hodo_ring", value_formatter=fstr)
    volume.description = "ft hodoscope support ring"
    volume.mother = "ft_hodo"
    volume.set_position(0, 0, VETO_RING_Z)
    volume.color = "cccccc"
    volume.make_tube(VETO_IR, VETO_RING_OR, VETO_RING_TN)
    volume.material = "ft_peek"
    volume.publish_passive(configuration)

    layer_z = -VETO_TN
    for layer, thickness in enumerate((7.0, 15.0), start=1):
        skin_half = 0.25
        layer_z += skin_half
        volume = GVolume(f"ft_hodo_L{layer}", value_formatter=fstr)
        volume.description = f"ft_hodo layer {layer} support"
        volume.mother = "ft_hodo_innervol"
        volume.set_position(0, 0, layer_z)
        volume.color = "EFEFFB"
        volume.make_tube(VETO_RING_OR, VETO_OR, skin_half)
        volume.material = "carbonFiber"
        volume.publish_passive(configuration)
        layer_z += skin_half
        painted_half = thickness / 2 + PAINT_TN
        layer_z += painted_half
        for quadrant in range(4):
            build_hodoscope_sector(
                configuration,
                layer,
                1 + 2 * quadrant,
                quadrant,
                layer_z,
                thickness / 2,
                painted_half,
                S1_X,
                S1_Y,
                S1_W,
            )
            build_hodoscope_sector(
                configuration,
                layer,
                2 + 2 * quadrant,
                quadrant,
                layer_z,
                thickness / 2,
                painted_half,
                S2_X,
                S2_Y,
                S2_W,
            )
        layer_z += painted_half


def build_hodoscope_sector(
    configuration,
    layer,
    sector,
    quadrant,
    z,
    tile_half,
    painted_half,
    x_positions,
    y_positions,
    width_multipliers,
):
    """Build all wrapped tiles belonging to one hodoscope octant."""
    pitch = 2 * (TILE_WIDTH + 2 * PAINT_TN)
    for component, (x_factor, y_factor, width) in enumerate(
        zip(x_positions, y_positions, width_multipliers),
        start=1,
    ):
        source_x = x_factor * pitch
        source_y = y_factor * pitch
        x, y = (
            (source_x, source_y),
            (-source_y, source_x),
            (-source_x, -source_y),
            (source_y, -source_x),
        )[quadrant]
        short = width == 1
        prefix = "ft_hodo_p15_" if short else "ft_hodo_p30_"
        tile_prefix = "ft_hodo_p15_tile_" if short else "ft_hodo_p30_tile_"
        color = "3399FF" if short else "0431B4"
        suffix = f"{sector}{layer}{component}"
        volume = GVolume(f"{prefix}{suffix}", value_formatter=fstr)
        volume.description = f"{prefix} {sector} {layer} {component}"
        volume.mother = "ft_hodo_innervol"
        volume.set_position(x, y, z)
        volume.color = color
        volume.make_box(
            width * (TILE_WIDTH + 2 * PAINT_TN) / 2,
            width * (TILE_WIDTH + 2 * PAINT_TN) / 2,
            painted_half,
        )
        volume.material = "G4_MYLAR"
        volume.publish_passive(configuration)
        volume = GVolume(f"{tile_prefix}{suffix}", value_formatter=fstr)
        volume.description = f"{tile_prefix} {sector} {layer} {component}"
        volume.mother = f"{prefix}{suffix}"
        volume.color = "BCA9F5"
        volume.make_box(width * TILE_WIDTH / 2, width * TILE_WIDTH / 2, tile_half)
        volume.material = "scintillator"
        volume.digitization = "ft_hodo"
        volume.set_identifier(*("sector", sector, "layer", layer, "component", component))
        volume.publish_passive(configuration)


# ---------------------------------------------------------------------------
# FTTRK
# ---------------------------------------------------------------------------

TRACKER_INNER = 60.0
TRACKER_OUTER = 170.0
TRACKER_Z0 = 1760.0
TRACKER_ZMIN = 1770.0
TRACKER_ZMAX = 1809.0
TRACKER_Z4 = 1810.6

EPOXY_DZ = 0.05
PCB_DZ = 0.1
STRIPS_DZ = 0.006
KAPTON_DZ = 0.0375
RESIST_STRIPS_DZ = 0.01
GAS1_DZ = 0.064
MESH_DZ = 0.009
PHOTORESIST_DZ = 0.032
ALUMINUM_RINGS_DZ = 2.5
DRIFT_ELECTRODE_DZ = 0.006
GAS2_DZ = ALUMINUM_RINGS_DZ - DRIFT_ELECTRODE_DZ
DRIFT_PCB_DZ = 0.1
DRIFT_GROUND_DZ = 0.0025
PROTECTION_DZ = 0.025
ASSEMBLY_DZ = (3.9, 3.9, 4.5)

ZREL = [0.0]
for half_thickness in (
    EPOXY_DZ,
    PCB_DZ,
    STRIPS_DZ,
    KAPTON_DZ,
    RESIST_STRIPS_DZ,
    GAS1_DZ,
    MESH_DZ,
    PHOTORESIST_DZ + GAS2_DZ,
    DRIFT_ELECTRODE_DZ,
    DRIFT_PCB_DZ,
    DRIFT_GROUND_DZ,
    PROTECTION_DZ,
):
    ZREL.append(ZREL[-1] + 2 * half_thickness)

TRACKER_LAYER_Z = [1774.0 + ZREL[12]]
TRACKER_LAYER_Z.append(TRACKER_LAYER_Z[0] + 2 * ZREL[9] + 2 * ASSEMBLY_DZ[2])

TRACKER_COLORS = {
    "epoxy": "e200e1",
    "pcboard": "0000ff",
    "strips": "353540",
    "gas": "e10000",
    "mesh": "252020",
    "photoresist": "d200d1",
    "drift": "fff600",
    "aluminum": "aaaaff",
}


def tracker_z(layer, side, lower, upper):
    """Return the absolute centre of a layer on the X (-) or Y (+) side."""
    sign = -1 if side == 1 else 1
    return TRACKER_LAYER_Z[layer] + sign * 0.5 * (lower + upper)


def tracker_axis(side):
    """Return the GEMC2 X/Y label for a tracker side."""
    return "X" if side == 1 else "Y"


def build_tracker(configuration):
    """Build the two Micromegas disks, support rings, and electronics boxes."""
    build_tracker_mother(configuration)
    for layer in range(2):
        for side in (1, 2):
            build_tracker_disk_side(configuration, layer, side)
    build_tracker_assembly(configuration)
    build_tracker_fee_boxes(configuration)


def build_tracker_mother(configuration):
    """Build the FTTRK mother polycone and four centring supports."""
    volume = GVolume("ft_trk", value_formatter=fstr)
    volume.description = "ft tracker micromegas"
    volume.color = "aaaaff"
    volume.make_polycone(
        zplane=(
            TRACKER_Z0,
            TRACKER_ZMIN,
            TRACKER_ZMIN,
            TRACKER_ZMAX,
            TRACKER_ZMAX,
            TRACKER_Z4,
        ),
        iradius=(40.0,) * 6,
        oradius=(59.75, 59.75, TRACKER_OUTER, TRACKER_OUTER, 50.0, 50.0),
    )
    volume.material = "G4_AIR"
    volume.visible = 0
    volume.publish_passive(configuration)
    zmin = (TRACKER_Z0, 1774.0, 1805.2, TRACKER_ZMIN)
    zmax = (1774.0, 1805.2, TRACKER_Z4, 1774.0)
    inner = (40.0, 40.0, 40.0, 59.75)
    outer = (59.75, 50.0, 50.0, 67.0)
    for ring in range(4):
        volume = GVolume(f"ft_trk_support_R{ring + 1}", value_formatter=fstr)
        volume.description = f"ft tracker centering support, ring {ring + 1}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, 0.5 * (zmax[ring] + zmin[ring]))
        volume.color = TRACKER_COLORS["aluminum"]
        volume.make_tube(inner[ring], outer[ring], 0.5 * (zmax[ring] - zmin[ring]))
        volume.material = "G4_Al"
        volume.publish_passive(configuration)


def build_tracker_disk_side(configuration, layer, side):
    """Build all material layers and aluminium rings on one side of a tracker disk."""
    layer_number = layer + 1
    axis = tracker_axis(side)
    simple_layers = (
        ("epoxy", "epoxy", 0, 1, EPOXY_DZ, TRACKER_INNER, TRACKER_OUTER, "epoxy", "epoxy"),
        ("pcboard", "pc board", 1, 2, PCB_DZ, TRACKER_INNER, TRACKER_OUTER, "myFR4", "pcboard"),
        ("strips", "strips", 2, 3, STRIPS_DZ, 70.43, 143.66, "mmstrips", "strips"),
        ("resiststrips", "resistive strips", 4, 5, RESIST_STRIPS_DZ, 70.43, 143.66,
         "ResistPaste", "strips"),
        ("gas1", "gas1", 5, 6, GAS1_DZ, 71.43, 143.16, "mmgas", "gas"),
        ("mesh", "mesh", 6, 7, MESH_DZ, TRACKER_INNER, TRACKER_OUTER, "mmmesh", "mesh"),
        ("driftel", "drift electrode", 8, 9, DRIFT_ELECTRODE_DZ, 70.43, 143.66,
         "G4_Cu", "strips"),
        ("drift", "drift", 9, 10, DRIFT_PCB_DZ, TRACKER_INNER, 158.5, "myFR4", "pcboard"),
    )
    for stem, description, lower, upper, half_length, inner, outer, material, color in simple_layers:
        volume = GVolume(f"ft_trk_{stem}_{axis}_L{layer_number}", value_formatter=fstr)
        volume.description = f"{description} {axis}, layer {layer_number}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, tracker_z(layer, side, ZREL[lower], ZREL[upper]))
        volume.color = TRACKER_COLORS[color]
        volume.make_tube(inner, outer, half_length)
        volume.material = material
        volume.publish_passive(configuration)

    build_tracker_kapton(configuration, layer, side)
    build_tracker_photoresist(configuration, layer, side)
    gas2_z = tracker_z(layer, side, ZREL[7] + 2 * PHOTORESIST_DZ, ZREL[8])
    volume = GVolume(f"ft_trk_gas2_{axis}_L{layer_number}", value_formatter=fstr)
    volume.description = f"gas2 {axis}, layer {layer_number}"
    volume.mother = "ft_trk"
    volume.set_position(0, 0, gas2_z)
    volume.color = TRACKER_COLORS["gas"]
    volume.make_tube(67.0, 151.5, GAS2_DZ)
    volume.material = "mmgas"
    volume.digitization = "ft_trk"
    volume.set_identifier(*(
    "superlayer",
    layer_number,
    "type",
    side,
    "segment",
    1,
    "strip",
    1,
))
    volume.publish_passive(configuration)
    build_tracker_rings(configuration, layer, side)


def build_tracker_kapton(configuration, layer, side):
    """Build the two Kapton annuli for one disk side."""
    layer_number = layer + 1
    axis = tracker_axis(side)
    zmin = (ZREL[3], ZREL[11])
    zmax = (ZREL[4], ZREL[12])
    outer = (TRACKER_OUTER, 158.5)
    for ring in range(2):
        volume = GVolume(f"ft_trk_kapton_{axis}_L{layer_number}_R{ring + 1}", value_formatter=fstr)
        volume.description = f"kapton {axis}, layer {layer_number}, ring {ring + 1}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, tracker_z(layer, side, zmin[ring], zmax[ring]))
        volume.color = TRACKER_COLORS["pcboard"]
        volume.make_tube(TRACKER_INNER, outer[ring], 0.5 * (zmax[ring] - zmin[ring]))
        volume.material = "G4_KAPTON"
        volume.publish_passive(configuration)


def build_tracker_photoresist(configuration, layer, side):
    """Build four photoresist annuli around the active gas."""
    layer_number = layer + 1
    axis = tracker_axis(side)
    zmin = (ZREL[5], ZREL[5], ZREL[7], ZREL[7])
    zmax = (
        ZREL[6],
        ZREL[6],
        ZREL[9] - 2 * ALUMINUM_RINGS_DZ,
        ZREL[9] - 2 * ALUMINUM_RINGS_DZ,
    )
    inner = (TRACKER_INNER, 143.16, TRACKER_INNER, 143.16)
    outer = (71.43, TRACKER_OUTER, 71.43, TRACKER_OUTER)
    for ring in range(4):
        volume = GVolume(f"ft_trk_phrst_{axis}_L{layer_number}_R{ring + 1}", value_formatter=fstr)
        volume.description = f"photoresist {axis}, layer {layer_number}, ring {ring + 1}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, tracker_z(layer, side, zmin[ring], zmax[ring]))
        volume.color = TRACKER_COLORS["photoresist"]
        volume.make_tube(inner[ring], outer[ring], 0.5 * (zmax[ring] - zmin[ring]))
        volume.material = "myPhRes"
        volume.publish_passive(configuration)


def build_tracker_rings(configuration, layer, side):
    """Build the two annuli and 25 outer extensions for one disk side."""
    layer_number = layer + 1
    axis = tracker_axis(side)
    name = f"ft_trk_ring_{axis}_L{layer_number}"
    zmin = ZREL[7] + 2 * PHOTORESIST_DZ
    zmax = ZREL[9]
    z = tracker_z(layer, side, zmin, zmax)
    for ring, (inner, outer) in enumerate(((60.0, 67.0), (151.5, 158.5)), start=1):
        volume = GVolume(f"{name}_R{ring}", value_formatter=fstr)
        volume.description = f"ring {axis}, layer {layer_number}, ring {ring}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, z)
        volume.color = TRACKER_COLORS["aluminum"]
        volume.make_tube(inner, outer, ALUMINUM_RINGS_DZ)
        volume.material = "G4_Al"
        volume.publish_passive(configuration)
    for extension in range(25):
        number = extension + 1
        start = -0.5 * 4.9 + extension * 15.0
        if number == 24:
            start -= 5.0
        if number == 25:
            start = start - 15.0 + 5.0
        volume = GVolume(f"{name}_E{number}", value_formatter=fstr)
        volume.description = f"ring {axis}, layer {layer_number}, ext {number}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, z)
        volume.color = TRACKER_COLORS["aluminum"]
        volume.make_tube(158.5, TRACKER_OUTER, ALUMINUM_RINGS_DZ, start, 4.9)
        volume.material = "G4_Al"
        volume.publish_passive(configuration)


def build_tracker_assembly(configuration):
    """Build the common three-ring tracker assembly and its radial branches."""
    inner = (60.0, 158.7, 163.5)
    outer = (67.0, 163.5, 170.0)
    zmin = ZREL[9]
    zmax = zmin + 2 * ASSEMBLY_DZ[2]
    z = TRACKER_LAYER_Z[0] + 0.5 * (zmin + zmax)
    for ring in range(3):
        volume = GVolume(f"ft_trk_assembly_R{ring + 1}", value_formatter=fstr)
        volume.description = f"assembly, ring {ring + 1}"
        volume.mother = "ft_trk"
        volume.set_position(0, 0, z)
        volume.color = TRACKER_COLORS["aluminum"]
        volume.make_tube(inner[ring], outer[ring], ASSEMBLY_DZ[ring])
        volume.material = "G4_Al"
        volume.publish_passive(configuration)

    dx = 0.5 * (158.69 - 67.0)
    dy = 1.5
    for branch in range(3):
        rotation = branch * 120.0
        radians = math.radians(rotation)
        volume = GVolume(f"ft_trk_assembly_B{branch + 1}", value_formatter=fstr)
        volume.description = f"assembly, branch {branch + 1}"
        volume.mother = "ft_trk"
        volume.set_position((67.0 + dx) * math.cos(radians), (67.0 + dx) * math.sin(radians), z)
        volume.rotations = [f'0*deg, 0*deg, {fstr(-rotation)}*deg']
        volume.color = TRACKER_COLORS["aluminum"]
        volume.make_box(dx, dy, ASSEMBLY_DZ[0])
        volume.material = "G4_Al"
        volume.publish_passive(configuration)


def build_tracker_fee_boxes(configuration):
    """Build the three electronics crates and internal flux/dose planes."""
    fee_width = 91.0 / 2
    fee_height = 265.5 / 2
    fee_length = 242.0 / 2
    fee_air = (fee_height - 1.5, fee_width - 1.5, fee_length - 1.5)
    arm_length = 530.0 / 2 - 80.0
    polar = -22.0
    for index, azimuth in enumerate((210.0, 270.0, 330.0)):
        polar_radians = polar / 57.27
        azimuth_radians = azimuth / 57.27
        arm_x = (200.0 + 2.0 + arm_length * math.cos(polar_radians)) * math.cos(azimuth_radians)
        arm_y = -(200.0 + 2.0 + arm_length * math.cos(polar_radians)) * math.sin(azimuth_radians)
        arm_z = B_LINE_Z5 + 0.1 + 1.0 + arm_length * math.sin(polar_radians)
        radius = ((arm_length - fee_height) * math.cos(polar_radians)
                  + (fee_length + 2.0 + 0.2) * math.sin(polar_radians))
        x = arm_x + radius * math.cos(azimuth_radians)
        y = arm_y - radius * math.sin(azimuth_radians)
        z = (arm_z + (arm_length - fee_height) * math.sin(polar_radians)
             - (fee_length + 2.0 + 0.2) * math.cos(polar_radians) - 50.0)
        rotation = f"ordered: zyx, {fstr(azimuth)}*deg, 0*deg, 0*deg"
        box_name = f"ft_trk_fee_box_{index}"
        air_name = f"ft_trk_fee_air_{index}"
        volume = GVolume(box_name, value_formatter=fstr)
        volume.description = f"ft-trk fee box {index}"
        volume.mother = "ft_cal"
        volume.set_position(x, y, z)
        volume.rotations = [rotation]
        volume.color = "999999"
        volume.make_box(fee_height, fee_width, fee_length)
        volume.material = "G4_Al"
        volume.publish_passive(configuration)
        volume = GVolume(air_name, value_formatter=fstr)
        volume.description = f"ft-trk fee air {index}"
        volume.mother = box_name
        volume.color = "CCFFFF"
        volume.make_box(*fee_air)
        volume.material = "G4_AIR"
        volume.publish_passive(configuration)
        volume = GVolume(f"ft_trk_fee_flux_1_{index}", value_formatter=fstr)
        volume.description = "ft-trk fee flux 1"
        volume.mother = air_name
        volume.set_position(0, 0, -fee_air[2] + 0.5)
        volume.color = "aa0088"
        volume.make_box(fee_air[0] - 1.0, fee_air[1] - 1.0, 0.5)
        volume.material = "G4_Galactic"
        volume.digitization = "flux"
        volume.set_identifier(*("id", 4))
        volume.publish_passive(configuration)
        volume = GVolume(f"ft_trk_fee_flux_2_{index}", value_formatter=fstr)
        volume.description = "ft-trk fee flux 2"
        volume.mother = air_name
        volume.set_position(0, -fee_width * 0.6, 0)
        volume.color = "aa0088"
        volume.make_box(fee_air[0] - 1.0, 0.5, fee_air[2] - 1.0)
        volume.material = "G4_Galactic"
        volume.digitization = "flux"
        volume.set_identifier(*("id", 5))
        volume.publish_passive(configuration)
        volume = GVolume(f"ft_trk_fee_dose_{index}", value_formatter=fstr)
        volume.description = "ft-trk fee dose"
        volume.mother = air_name
        volume.color = "003300"
        volume.make_box(fee_air[0] - 5.0, 5.0, fee_air[2] - 5.0)
        volume.material = "scintillator"
        volume.publish_passive(configuration)
