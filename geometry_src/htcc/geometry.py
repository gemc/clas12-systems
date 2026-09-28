"""HTCC native-volume geometry, ported from clas12Tags geometry_source/htcc.

Ported perl scripts: geo/mother.pl (gas volume + windows), geo/mirrors.pl (48 elliptical
mirrors built from boolean cuts of a polycone barrel and an ellipsoid front surface), and
geo/pmts.pl (48 PMTs + 48 Winston-cone paraboloid shells). Shape parameters come from
`htcc__parameters_default.txt`; all other constants are hard-coded exactly as in the perl.

Numeric strings reproduce the perl `sprintf` field widths used in each script
(`%14.10g` in mirrors.pl, `%15.8g` for the PMT placements, `%12.8g` for the Winston-cone
dimensions) so the generated geometry matches the clas12Tags references.

Optical mirror/Winston-cone volumes are passive: they carry the `htcc_AlMgF2` skin surface
(mirrors.py) through `GVolume.mirror`. Only the PMT quartz volumes are sensitive (`htcc`).
"""

import math

from pygemc import GVolume

from htcc_parameters import load_parameters


PI = math.pi

# Small global z-shift of the gas volume and windows per configuration (mother.pl).
CONFIG_Z_SHIFT = {
    "default": 0.0,
    "rga_spring2018": -10.0,
    "rga_fall2018": -19.4,
}

COLORS_EVEN = ("ff8080", "8080ff", "80ff80", "f0f0f0")

MIRROR_SURFACE = "htcc_AlMgF2"


# ---------------------------------------------------------------------------
# formatting + small vector helpers
# ---------------------------------------------------------------------------
def s15(value):
    return ("%15.8g" % float(value)).strip()


def s14(value):
    return ("%14.10g" % float(value)).strip()


def s12(value):
    return ("%12.8g" % float(value)).strip()


def num(value):
    """Perl default number stringification (%.15g)."""
    text = "%.15g" % float(value)
    return "0" if text == "-0" else text


def _sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _mag(a):
    return math.sqrt(a[0] * a[0] + a[1] * a[1] + a[2] * a[2])


def _rotz_dividing(point, ang):
    """Rotate a dividing-plane point about z as mirrors.pl does (x cos - y sin, ...)."""
    x, y, z = point
    return (
        x * math.cos(ang) - y * math.sin(ang),
        y * math.cos(ang) + x * math.sin(ang),
        z,
    )


def _plane_unitnormal(p1, p2, p3):
    """Unit normal to the plane through p1,p2,p3, forced to point along +z."""
    vec21 = _sub(p1, p2)
    vec23 = _sub(p3, p2)
    cross = _cross(vec21, vec23)
    mag = _mag(cross)
    n = [cross[0] / mag, cross[1] / mag, cross[2] / mag]
    if n[2] < 0.0:
        n = [-n[0], -n[1], -n[2]]
    return n


def new_volume(name, mother="htcc"):
    volume = GVolume(name)
    volume.mother = mother
    return volume


def component_volume(name, mother="htcc"):
    volume = new_volume(name, mother)
    volume.material = "Component"
    return volume


def operation(volume, opr, parameters="0", absolute=False):
    """Mark volume as a GEMC2 boolean of already-placed component solids.

    `absolute=True` reproduces GEMC2's `Operation:@`: the operand positions/rotations are given in the
    common mother frame, so the second solid's transform accounts for the first solid's own rotation and
    position. It is encoded as a leading "@" token in solidsOpr, which the gemc native boolean builder
    parses. Booleans whose first operand is at the origin with no rotation give the same result either way.
    """
    volume.solidsOpr = f"@ {opr}" if absolute else opr
    volume.parameters = parameters
    return volume


# ---------------------------------------------------------------------------
# utils.pl — element naming and identity
# ---------------------------------------------------------------------------
def _sector_of(sindex, hindex):
    if hindex == 1:
        return (sindex + 2) % 6 + 1
    return (sindex + 1) % 6 + 1


def htcc_name(element, sindex, rindex, hindex):
    ring_index = 4 - rindex
    sector = _sector_of(sindex, hindex)
    return f"{element}_{ring_index}_sector{sector}_{hindex}"


def htcc_desc(element, sindex, rindex, hindex):
    ring_index = 4 - rindex
    sector = _sector_of(sindex, hindex)
    half = "right" if hindex == 2 else "left"
    return f"htcc {element} {ring_index}, sector{sector} {half}"


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------
def build_htcc(configuration):
    """Publish all HTCC native volumes for the variation selected in configuration."""
    pars = load_parameters()
    build_mother(configuration)
    build_mirrors(configuration, pars)
    build_pmts(configuration)


# ---------------------------------------------------------------------------
# cad/cad_<variation>.gxml — the three beamline cones as CAD meshes
# ---------------------------------------------------------------------------
# GEMC2 places these under `root` at the detector-survey z (same shift as the gas volume); the Moller cone
# extension is nudged +1 mm in z to avoid overlapping the Moller cone. Meshes live in stls/ and are built by
# build_cad_meshes.py. Published to the separate `htcc_cad` CAD system (see htcc.py) because gemc4 chooses the
# mesh builder per system.
CAD_CONES = ("htccMollerConeExt", "htccMollerCone", "htccCone")


def build_cad(configuration):
    """Publish the three HTCC CAD cones for the variation selected in configuration."""
    zshift_cm = CONFIG_Z_SHIFT[configuration.variation] / 10.0
    for name in CAD_CONES:
        # 1 mm (0.1 cm) added to the extension to avoid overlap with the Moller cone (GEMC2 gxml).
        zpos_cm = zshift_cm + 0.1 if name == "htccMollerConeExt" else zshift_cm
        cone = GVolume(name)
        cone.mother = "root"
        cone.solid = "CAD"
        cone.parameters = f"stls/{name}.stl, 1"
        cone.description = f"HTCC {name} CAD cone"
        cone.material = "rohacell31"
        cone.color = "888888"
        cone.position = f"0*cm, 0*cm, {num(zpos_cm)}*cm"
        cone.rotations = ["0*deg, 180*deg, 0*deg"]
        cone.publish_passive(configuration)


# ---------------------------------------------------------------------------
# mother.pl — gas volume (polycone booleans) + entry/exit windows
# ---------------------------------------------------------------------------
ENTRYDISH_Z = [
    -276.4122, -178.6222, -87.1822, 4.2578, 95.6978, 187.1378, 278.5778,
    370.0178, 461.4578, 552.8978, 644.3378, 735.7778, 827.2178, 918.6578,
    991.378, 1080.278, 1107.71,
]
ENTRYDISH_ROUTER = [
    1416.05, 1410.081, 1404.493, 1398.905, 1393.317, 1387.729, 1387.729,
    1363.4466, 1339.1388, 1305.8648, 1272.5908, 1239.3168, 1206.0174,
    1158.24, 1105.408, 996.0356, 945.896,
]
ENTRYCONE_Z = [400.00, 470.17, 561.61, 653.05, 744.49, 835.93, 927.37, 1018.81, 1116.6]
# Router modified to accommodate CTOF (first plane 235 instead of 257.505):
ENTRYCONE_ROUTER = [235, 323.952, 390.373, 456.819, 525.831, 599.872, 673.913, 747.979, 827.151]


def build_mother(configuration):
    zshift = CONFIG_Z_SHIFT[configuration.variation]

    big = component_volume("htccBigGasVolume", mother="root")
    big.description = "volume containing cherenkov gas"
    big.color = "ee99ff"  # GEMC2 "ee99ff5"; transparency digit dropped (pygemc takes 6-hex)
    big.make_polycone(
        0, 360,
        zplane=[-275, 181, 1046, 1740],
        iradius=[0, 15.8, 91.5, 150],
        oradius=[1742, 2300, 2300, 1589],
    )
    big.publish_passive(configuration)

    dish = component_volume("htccEntryDishVolume", mother="root")
    dish.description = "HTCC entry dish volume"
    dish.color = "ee99ff"
    dish.make_polycone(
        0, 360,
        zplane=ENTRYDISH_Z,
        iradius=[0] * len(ENTRYDISH_Z),
        oradius=ENTRYDISH_ROUTER,
    )
    dish.publish_passive(configuration)

    cone = component_volume("htccEntryConeVolume", mother="root")
    cone.description = "HTCC entry cone volume"
    cone.make_polycone(
        0, 360,
        zplane=ENTRYCONE_Z,
        iradius=[0] * len(ENTRYCONE_Z),
        oradius=ENTRYCONE_ROUTER,
    )
    cone.publish_passive(configuration)

    dishcone = component_volume("htccEntryDishCone", mother="root")
    dishcone.description = "subtraction entry dish - cone"
    operation(dishcone, "htccEntryDishVolume - htccEntryConeVolume",
              absolute=True).publish_passive(configuration)

    gas = new_volume("htcc", mother="root")
    gas.description = "gas volume for htcc"
    gas.color = "0000ff"  # GEMC2 "0000ff3"; transparency digit dropped (pygemc takes 6-hex)
    gas.position = f"0*mm, 0*mm, {num(zshift)}*mm"
    gas.material = "HTCCgas"
    gas.visible = 0
    gas.style = 1
    operation(gas, "htccBigGasVolume - htccEntryDishCone",
              absolute=True).publish_passive(configuration)

    # windows (thickness 38+75+38 microns tedlar/mylar/tedlar = 0.151 mm)
    window_half_thickness = 0.151 / 2.0

    exit_window = new_volume("htccExitWindow", mother="root")
    exit_window.description = "htcc Exit Window"
    exit_window.color = "666655"
    exit_window.position = f"0*mm, 0*mm, {num(1750 + zshift)}*mm"
    exit_window.material = "HTCCCompositeWindow"
    exit_window.style = 1
    exit_window.make_tube(277.622 / 2.0 + 1.5, 2895.6 / 2.0, window_half_thickness, 0, 360)
    exit_window.publish_passive(configuration)

    entry_window = new_volume("htccEntryWindow", mother="root")
    entry_window.description = "htcc Entry Window"
    entry_window.color = "666655"
    entry_window.position = f"0*mm, 0*mm, {num(380 + zshift)}*mm"
    entry_window.material = "HTCCCompositeWindow"
    entry_window.style = 1
    entry_window.make_tube(33, 278, window_half_thickness, 0, 360)
    entry_window.publish_passive(configuration)


# ---------------------------------------------------------------------------
# mirrors.pl — 48 elliptical mirrors, each a chain of boolean cuts
# ---------------------------------------------------------------------------
NZPLANES = 21
ZPLANES_MIRRORBACK = [
    360.01139, 423.09863, 486.18587, 549.27312, 612.36036, 675.4476, 738.53484,
    801.62208, 864.70932, 927.79656, 990.8838, 1053.971, 1117.0583, 1180.1455,
    1243.2328, 1306.32, 1369.4073, 1432.4945, 1495.5817, 1558.669, 1621.7562,
]
ROUTER_MIRRORBACK = [
    1435.3392, 1461.162, 1483.4626, 1502.4172, 1518.1665, 1530.8215, 1540.4676,
    1547.168, 1550.9654, 1551.8836, 1549.9283, 1545.0874, 1537.3303, 1526.6071,
    1512.8469, 1495.9556, 1475.8119, 1452.2631, 1425.1181, 1394.1386, 1359.0258,
]

PHI0 = 15.0 * PI / 180.0
PHISTEP = 60.0 * PI / 180.0


def _dividing_points(pars, prefix):
    """Three (x,y,z) dividing-plane points, e.g. prefix='M12L' → M12Lx1..M12Lz3."""
    return [
        (pars[f"{prefix}x{p}"], pars[f"{prefix}y{p}"], pars[f"{prefix}z{p}"])
        for p in (1, 2, 3)
    ]


def _ordered_yzx(phi, theta):
    return [f"ordered: yzx, 0*rad, {phi}*rad, {theta}*rad"]


def build_mirrors(configuration, pars):
    router_cut = pars["Routercut"]
    theta_axis = pars["thetabarrelaxis"] * PI / 180.0

    a = [pars[f"M{m}a"] for m in (1, 2, 3, 4)]
    b = [pars[f"M{m}b"] for m in (1, 2, 3, 4)]
    xfp = 0.0
    yfp = [pars[f"yfp{m}"] for m in (1, 2, 3, 4)]
    zfp = [pars[f"zfp{m}"] for m in (1, 2, 3, 4)]

    dp_left = {
        (1, 2): _dividing_points(pars, "M12L"),
        (2, 3): _dividing_points(pars, "M23L"),
        (3, 4): _dividing_points(pars, "M34L"),
    }
    dp_right = {
        (1, 2): _dividing_points(pars, "M12R"),
        (2, 3): _dividing_points(pars, "M23R"),
        (3, 4): _dividing_points(pars, "M34R"),
    }

    # outer edge of the largest-angle mirrors
    outer_cyl = component_volume("HTCC_OuterCutCylinder")
    outer_cyl.description = "Outer cut cylinder"
    outer_cyl.position = "0*mm, 0*mm, 1500*mm"
    outer_cyl.make_tube(router_cut, 1500.0, 500, 0, 360)
    outer_cyl.publish_passive(configuration)

    # inner edge of the smallest-angle mirrors (5 deg cone)
    inner_cone = component_volume("HTCC_InnerCutCone")
    inner_cone.description = "Inner cut cone"
    inner_cone.position = "0*mm, 0*mm, 1000*mm"
    inner_cone.make_cons(0.0, 0.0, 0.0, 174.97733, 1000.0, 0, 360)
    inner_cone.publish_passive(configuration)

    for i in range(6):
        for k in range(2):
            phirot = -PHI0 * (2.0 * k - 1.0) - PHISTEP * i
            if phirot < -PI:
                phirot += 2.0 * PI
            sphirot = s14(phirot)
            stheta = s14(theta_axis)

            # barrel defining the common back surface of the four mirrors
            barrel = component_volume(f"Barrel_sect{i}half{k}")
            barrel.description = "Barrel defining mirror back surface"
            barrel.rotations = _ordered_yzx(sphirot, stheta)
            barrel.make_polycone(
                0, 360,
                zplane=ZPLANES_MIRRORBACK,
                iradius=[0] * NZPLANES,
                oradius=ROUTER_MIRRORBACK,
            )
            barrel.publish_passive(configuration)

            # phi wedge that trims all four mirrors to half-sector width
            phistart_cut = PI / 2.0 + PHI0 * (2.0 * k - 2.0) + PHISTEP * i
            if phistart_cut > 2.0 * PI:
                phistart_cut -= 2.0 * PI
            dphi_cut = 0.5 * PHISTEP - 0.001  # microgap between mirrors

            phicut = component_volume(f"phicut_sect{i}half{k}")
            phicut.description = "Half-sector phi cut"
            phicut.position = "0*mm, 0*mm, 1500*mm"
            phicut.make_tube(0.0, 1500.0, 500.0, s14(phistart_cut), s14(dphi_cut),
                             lunit2="rad")
            phicut.publish_passive(configuration)

            for j in range(4):
                color_index = 2 * (k % 2) + j % 2

                # ellipsoid front surface: major axis along the ray to the 2nd focal point
                axis = (
                    xfp * math.cos(phirot) + yfp[j] * math.sin(phirot),
                    yfp[j] * math.cos(phirot) - xfp * math.sin(phirot),
                    zfp[j],
                )
                mag = _mag(axis)
                unitaxis = (axis[0] / mag, axis[1] / mag, axis[2] / mag)
                center = (0.5 * axis[0], 0.5 * axis[1], 0.5 * axis[2])
                sangle = s14(math.acos(unitaxis[2]))
                sphiellipse = s14(math.atan2(unitaxis[0], unitaxis[1]))

                ellipsoid = component_volume(f"Mirror_sect{i}mirr{j}half{k}")
                ellipsoid.description = "Ellipsoid defining mirror surface"
                ellipsoid.position = (
                    f"{s14(center[0])}*mm, {s14(center[1])}*mm, {s14(center[2])}*mm"
                )
                ellipsoid.rotations = _ordered_yzx(sphiellipse, sangle)
                ellipsoid.solid = "G4Ellipsoid"
                ellipsoid.parameters = (
                    f"{num(b[j])}*mm, {num(b[j])}*mm, {num(a[j])}*mm, 0*mm, 0*mm"
                )
                ellipsoid.publish_passive(configuration)

                # barrel - ellipsoid, evaluated at the barrel placement
                barrel_ellipse = component_volume(f"BarrelEllipseCut_sect{i}mirr{j}half{k}")
                barrel_ellipse.description = "subtraction of barrel and ellipse"
                barrel_ellipse.rotations = _ordered_yzx(sphirot, stheta)
                operation(
                    barrel_ellipse,
                    f"Barrel_sect{i}half{k} - Mirror_sect{i}mirr{j}half{k}",
                    absolute=True,
                ).publish_passive(configuration)

                if j == 0:
                    _build_mirror_bottom(configuration, i, j, k, sphirot, stheta,
                                         color_index, dp_left, dp_right)
                elif j in (1, 2):
                    _build_mirror_middle(configuration, i, j, k, sphirot, stheta,
                                         color_index, dp_left, dp_right)
                else:
                    _build_mirror_top(configuration, i, j, k, sphirot, stheta,
                                      color_index, dp_left, dp_right)


def _final_mirror(configuration, i, j, k, sphirot, stheta, color_index, opr):
    mirror = new_volume(htcc_name("mirror", i, j, (k + 1) % 2 + 1))
    mirror.description = htcc_desc("mirror", i, j, (k + 1) % 2 + 1)
    mirror.rotations = _ordered_yzx(sphirot, stheta)
    mirror.color = COLORS_EVEN[color_index]
    mirror.style = 1
    mirror.material = "rohacell31"
    mirror.mirror = MIRROR_SURFACE
    operation(mirror, opr, absolute=True).publish_passive(configuration)


def _box_cut(configuration, name, description, pos, phi, angle, width=1000.0):
    box = component_volume(name)
    box.description = description
    box.position = pos
    box.rotations = [f"ordered: yzx, 0*rad, {s14(phi)}*rad, {s14(angle)}*rad"]
    box.make_box(width, width, width)
    box.publish_passive(configuration)


# mirror 1 (j==0): cylindrical outer cut and the 1/2 lower dividing plane
def _build_mirror_bottom(configuration, i, j, k, sphirot, stheta, color_index,
                         dp_left, dp_right):
    points = dp_left[(1, 2)] if k == 0 else dp_right[(1, 2)]
    p1, p2, p3 = (_rotz_dividing(p, i * PHISTEP) for p in points)
    normal = _plane_unitnormal(p1, p2, p3)

    boxwidth = 1000.0
    vertical_microgap = 0.1
    boxpos = (
        p2[0] - boxwidth * normal[0],
        p2[1] - boxwidth * normal[1],
        p2[2] - boxwidth * normal[2] + vertical_microgap,
    )
    angle = math.acos(normal[2])
    phi = math.atan2(normal[0], normal[1])
    _box_cut(
        configuration, f"Boxcut12_sect{i}mirr{j}half{k}",
        "Box defining dividing plane 1/2",
        f"{s14(boxpos[0])}*mm, {s14(boxpos[1])}*mm, {s14(boxpos[2])}*mm",
        phi, angle,
    )

    box_cut = component_volume(f"MirrorBoxCut_sect{i}mirr{j}half{k}")
    box_cut.description = "subtraction of box and (barrel - ellipse)"
    box_cut.rotations = _ordered_yzx(sphirot, stheta)
    operation(
        box_cut,
        f"BarrelEllipseCut_sect{i}mirr{j}half{k} - Boxcut12_sect{i}mirr{j}half{k}",
        absolute=True,
    ).publish_passive(configuration)

    cyl_cut = component_volume(f"MirrorCylinderCut_sect{i}mirr{j}half{k}")
    cyl_cut.description = "subtraction of cylinder and (box - (barrel - ellipse))"
    cyl_cut.rotations = _ordered_yzx(sphirot, stheta)
    operation(
        cyl_cut,
        f"MirrorBoxCut_sect{i}mirr{j}half{k} - HTCC_OuterCutCylinder",
        absolute=True,
    ).publish_passive(configuration)

    _final_mirror(
        configuration, i, j, k, sphirot, stheta, color_index,
        f"MirrorCylinderCut_sect{i}mirr{j}half{k} * phicut_sect{i}half{k}",
    )


# mirrors 2,3 (j==1,2): upper and lower dividing planes
def _build_mirror_middle(configuration, i, j, k, sphirot, stheta, color_index,
                         dp_left, dp_right):
    dp = dp_left if k == 0 else dp_right
    upper = dp[(1, 2)] if j == 1 else dp[(2, 3)]
    lower = dp[(2, 3)] if j == 1 else dp[(3, 4)]

    up = [_rotz_dividing(p, i * PHISTEP) for p in upper]
    lo = [_rotz_dividing(p, i * PHISTEP) for p in lower]
    n_up = _plane_unitnormal(up[0], up[1], up[2])
    n_lo = _plane_unitnormal(lo[0], lo[1], lo[2])

    boxwidth = 1000.0
    up_pos = (
        up[1][0] + boxwidth * n_up[0],
        up[1][1] + boxwidth * n_up[1],
        up[1][2] + boxwidth * n_up[2],
    )
    _box_cut(
        configuration, f"Boxcut_up_sect{i}mirr{j}half{k}", "upper plane cut",
        f"{s14(up_pos[0])}*mm, {s14(up_pos[1])}*mm, {s14(up_pos[2])}*mm",
        math.atan2(n_up[0], n_up[1]), math.acos(n_up[2]),
    )

    vertical_microgap = 0.1
    lo_pos = (
        lo[1][0] - boxwidth * n_lo[0],
        lo[1][1] - boxwidth * n_lo[1],
        lo[1][2] - boxwidth * n_lo[2] + vertical_microgap,
    )
    _box_cut(
        configuration, f"Boxcut_down_sect{i}mirr{j}half{k}", "lower plane cut",
        f"{s14(lo_pos[0])}*mm, {s14(lo_pos[1])}*mm, {s14(lo_pos[2])}*mm",
        math.atan2(n_lo[0], n_lo[1]), math.acos(n_lo[2]),
    )

    up_cut = component_volume(f"MirrorBoxCut_up_sect{i}mirr{j}half{k}")
    up_cut.description = "subtraction of upper box from (barrel - ellipse)"
    up_cut.rotations = _ordered_yzx(sphirot, stheta)
    operation(
        up_cut,
        f"BarrelEllipseCut_sect{i}mirr{j}half{k} - Boxcut_up_sect{i}mirr{j}half{k}",
        absolute=True,
    ).publish_passive(configuration)

    down_cut = component_volume(f"MirrorBoxCut_down_sect{i}mirr{j}half{k}")
    down_cut.description = "subtraction of lower box from (barrel - ellipse - upper box)"
    down_cut.rotations = _ordered_yzx(sphirot, stheta)
    operation(
        down_cut,
        f"MirrorBoxCut_up_sect{i}mirr{j}half{k} - Boxcut_down_sect{i}mirr{j}half{k}",
        absolute=True,
    ).publish_passive(configuration)

    _final_mirror(
        configuration, i, j, k, sphirot, stheta, color_index,
        f"MirrorBoxCut_down_sect{i}mirr{j}half{k} * phicut_sect{i}half{k}",
    )


# mirror 4 (j==3): upper dividing plane and the inner theta cone
def _build_mirror_top(configuration, i, j, k, sphirot, stheta, color_index,
                      dp_left, dp_right):
    points = dp_left[(3, 4)] if k == 0 else dp_right[(3, 4)]
    p1, p2, p3 = (_rotz_dividing(p, i * PHISTEP) for p in points)
    normal = _plane_unitnormal(p1, p2, p3)

    boxwidth = 1000.0
    boxpos = (
        p2[0] + boxwidth * normal[0],
        p2[1] + boxwidth * normal[1],
        p2[2] + boxwidth * normal[2],
    )
    _box_cut(
        configuration, f"Boxcut_up_sect{i}mirr{j}half{k}", "upper plane cut",
        f"{s14(boxpos[0])}*mm, {s14(boxpos[1])}*mm, {s14(boxpos[2])}*mm",
        math.atan2(normal[0], normal[1]), math.acos(normal[2]),
    )

    up_cut = component_volume(f"MirrorBoxCut_up_sect{i}mirr{j}half{k}")
    up_cut.description = "subtraction of upper box from (barrel - ellipse)"
    up_cut.rotations = _ordered_yzx(sphirot, stheta)
    operation(
        up_cut,
        f"BarrelEllipseCut_sect{i}mirr{j}half{k} - Boxcut_up_sect{i}mirr{j}half{k}",
        absolute=True,
    ).publish_passive(configuration)

    cone_cut = component_volume(f"MirrorConeCut_sect{i}mirr{j}half{k}")
    cone_cut.description = "subtraction of lower cone from (barrel - ellipse - box)"
    cone_cut.rotations = _ordered_yzx(sphirot, stheta)
    operation(
        cone_cut,
        f"MirrorBoxCut_up_sect{i}mirr{j}half{k} - HTCC_InnerCutCone",
        absolute=True,
    ).publish_passive(configuration)

    _final_mirror(
        configuration, i, j, k, sphirot, stheta, color_index,
        f"MirrorConeCut_sect{i}mirr{j}half{k} * phicut_sect{i}half{k}",
    )


# ---------------------------------------------------------------------------
# pmts.pl — 48 sensitive PMTs and 48 Winston-cone paraboloid shells
# ---------------------------------------------------------------------------
SECTORPHIRAD = 60.0 * PI / 180.0

PMT_RADIUS = 55.0
PMT_LENGTH = 3.0
PMT_DZ = PMT_LENGTH / 2.0

WC_R1 = 55.0
WC_R2 = 74.1426
WC_Z1 = 233.0
WC_Z2 = 423.5
WC_DZ = 0.5 * (WC_Z2 - WC_Z1)
WC_DZD = WC_DZ + 30.0
WC_K2 = (WC_R1 ** 2 + WC_R2 ** 2) / 2.0
WC_K1 = (WC_R2 ** 2 - WC_R1 ** 2) / (2.0 * WC_DZ)
WC_R1D = math.sqrt(WC_K2 - WC_DZD * WC_K1)
WC_R2D = math.sqrt(WC_K2 + WC_DZD * WC_K1)

FOCALPOINTS_LEFT = [
    [417.483, 1558.067, -62.047],
    [462.948, 1727.744, 163.333],
    [492.379, 1837.584, 425.482],
    [503.907, 1880.607, 707.739],
]
FOCALPOINTS_RIGHT = [[-p[0], p[1], p[2]] for p in FOCALPOINTS_LEFT]

DIRECTION_LEFT_DEG = [
    [85.2787, 72.1106, 161.4570],
    [81.6072, 56.9940, 145.6710],
    [78.6436, 42.7025, 130.4645],
    [76.5506, 29.7704, 116.0198],
]
DIRECTION_RIGHT_DEG = [
    [94.7213, 72.1106, 161.4570],
    [98.3928, 56.9940, 145.6710],
    [101.3564, 42.7025, 130.4645],
    [103.4494, 29.7704, 116.0198],
]


def _unit_vectors(direction_deg):
    vectors = []
    for angles in direction_deg:
        v = [math.cos(angle * PI / 180.0) for angle in angles]
        sumsq = sum(component * component for component in v)
        inv = 1.0 / math.sqrt(sumsq)
        vectors.append([component * inv for component in v])
    return vectors


UNITVECTORS_LEFT = _unit_vectors(DIRECTION_LEFT_DEG)
UNITVECTORS_RIGHT = _unit_vectors(DIRECTION_RIGHT_DEG)

PMTPOS_LEFT = [
    [FOCALPOINTS_LEFT[j][m] + UNITVECTORS_LEFT[j][m] * PMT_LENGTH / 2.0 for m in range(3)]
    for j in range(4)
]
PMTPOS_RIGHT = [
    [FOCALPOINTS_RIGHT[j][m] + UNITVECTORS_RIGHT[j][m] * PMT_LENGTH / 2.0 for m in range(3)]
    for j in range(4)
]
WCPOS_LEFT = [
    [FOCALPOINTS_LEFT[j][m] - UNITVECTORS_LEFT[j][m] * WC_DZ for m in range(3)]
    for j in range(4)
]
WCPOS_RIGHT = [
    [FOCALPOINTS_RIGHT[j][m] - UNITVECTORS_RIGHT[j][m] * WC_DZ for m in range(3)]
    for j in range(4)
]


def _rotz_phi(vec, phi):
    """Rotate (x,y) about z by phi (pmts.pl convention: x cos - y sin, x sin + y cos)."""
    return [
        vec[0] * math.cos(phi) - vec[1] * math.sin(phi),
        vec[0] * math.sin(phi) + vec[1] * math.cos(phi),
        vec[2],
    ]


def build_pmts(configuration):
    for i in range(6):
        phitemp = SECTORPHIRAD * i
        for j in range(4):
            uvl = _rotz_phi(UNITVECTORS_LEFT[j], phitemp)
            uvr = _rotz_phi(UNITVECTORS_RIGHT[j], phitemp)
            pos_left = _rotz_phi(PMTPOS_LEFT[j], phitemp)
            pos_right = _rotz_phi(PMTPOS_RIGHT[j], phitemp)

            # rotation angles to point the PMT cylinder along its orientation vector.
            # The alpha_y bug in pmts.pl (uvr[2] used for both) is harmless because the
            # left/right z-components are equal, but it is preserved verbatim.
            alpha_x_left = math.atan2(uvl[1], uvl[2])
            alpha_x_right = math.atan2(uvr[1], uvr[2])
            alpha_y_left = -math.atan2(uvl[0], math.sqrt(uvl[1] ** 2 + uvr[2] ** 2))
            alpha_y_right = -math.atan2(uvr[0], math.sqrt(uvr[1] ** 2 + uvr[2] ** 2))

            # left pmt (hindex 1): position/rotation from the RIGHT arrays (perl quirk)
            _build_pmt(
                configuration, i, j, 1, pos_right,
                alpha_x_right * 180.0 / PI, alpha_y_right * 180.0 / PI,
                COLORS_EVEN[(j % 2) + 2],
            )
            # right pmt (hindex 2): position/rotation from the LEFT arrays
            _build_pmt(
                configuration, i, j, 2, pos_left,
                alpha_x_left * 180.0 / PI, alpha_y_left * 180.0 / PI,
                COLORS_EVEN[j % 2],
            )

            # Winston cones: orientation vector is opposite to the PMT
            uvl_wc = [-c for c in uvl]
            uvr_wc = [-c for c in uvr]
            wc_pos_left = _rotz_phi(WCPOS_LEFT[j], phitemp)
            wc_pos_right = _rotz_phi(WCPOS_RIGHT[j], phitemp)

            wc_alpha_x_left = math.atan2(uvl_wc[1], uvl_wc[2])
            wc_alpha_x_right = math.atan2(uvr_wc[1], uvr_wc[2])
            wc_alpha_y_left = -math.atan2(uvl_wc[0], math.sqrt(uvl_wc[1] ** 2 + uvr_wc[2] ** 2))
            wc_alpha_y_right = -math.atan2(uvr_wc[0], math.sqrt(uvr_wc[1] ** 2 + uvr_wc[2] ** 2))

            _build_wc_shell(
                configuration, htcc_name("wc", i, j, 1), htcc_desc("wc", i, j, 1),
                wc_pos_right, wc_alpha_x_right * 180.0 / PI, wc_alpha_y_right * 180.0 / PI,
                COLORS_EVEN[2 + (j % 2)],
            )
            _build_wc_shell(
                configuration, htcc_name("wc", i, j, 2), htcc_desc("wc", i, j, 2),
                wc_pos_left, wc_alpha_x_left * 180.0 / PI, wc_alpha_y_left * 180.0 / PI,
                COLORS_EVEN[j % 2],
            )


def _build_pmt(configuration, i, j, hindex, pos, xrot, yrot, color):
    pmt = new_volume(htcc_name("pmt", i, j, hindex))
    pmt.description = htcc_desc("pmt", i, j, hindex)
    pmt.position = f"{s15(pos[0])}*mm, {s15(pos[1])}*mm, {s15(pos[2])}*mm"
    pmt.rotations = [f"{s15(xrot)}*deg, {s15(yrot)}*deg, {s15(0.0)}*deg"]
    pmt.color = color
    pmt.make_tube(0, PMT_RADIUS, PMT_DZ, 0, 360)
    pmt.material = "HTCCPMTQuartz"
    pmt.style = 1
    pmt.digitization = "htcc"
    ring = 4 - j
    sector = _sector_of(i, hindex)
    pmt.set_identifier("sector", sector, "ring", ring, "half", hindex)
    pmt.publish_passive(configuration)


def _build_wc_shell(configuration, name, description, pos, xrot, yrot, color):
    pos_str = f"{s15(pos[0])}*mm, {s15(pos[1])}*mm, {s15(pos[2])}*mm"
    rot = [f"{s15(xrot)}*deg, {s15(yrot)}*deg, {s15(0.0)}*deg"]

    inner = component_volume(f"{name}inner")
    inner.description = f"{description}inner"
    inner.make_paraboloid(s12(WC_DZD), s12(WC_R1D), s12(WC_R2D))
    inner.publish_passive(configuration)

    outer = component_volume(f"{name}outer")
    outer.description = f"{description}outer"
    outer.position = pos_str
    outer.rotations = rot
    outer.make_paraboloid(s12(WC_DZ), s12(WC_R1 + 1.0), s12(WC_R2 + 1.0))
    outer.publish_passive(configuration)

    shell = new_volume(name)
    shell.description = description
    shell.position = pos_str
    shell.rotations = rot
    shell.color = color
    shell.material = "G4_Al"
    shell.mirror = MIRROR_SURFACE
    shell.style = 0
    shell.visible = 0
    operation(shell, f"{name}outer - {name}inner").publish_passive(configuration)
