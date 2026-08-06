#!/usr/bin/env python3
"""Regenerate the LTCC CAD meshes in stls/ and (re)write the gcad placement YAML.

    python build_cad_meshes.py          # rebuild the STL meshes into stls/
    python build_cad_meshes.py --yaml   # (re)write stls/cad__default.yaml

Run with the pygemc source on the path:
    PYTHONPATH=../../../pygemc/src python3 build_cad_meshes.py

Meshes:
  WC_{S,M,L}  Winston-cone mirrors, cured + decimated from clas12Tags cad/.
  backwall    S1-BW + S1-TB + S1-BB, merged into one watertight solid (sector-3 frame back assembly).
  rightwall   S1-RW + S1-BRB + S1-TRB, merged into one watertight solid (sector-3 frame right side).
  leftwall    rightwall mirrored across the detector centre plane (phi = 120 deg), same placement.
  nose        Epoxy + FrontPlate + Mount + Nose as a segmented convex hull (finer at the neck) plus
              NFrame as a flat slab, unioned, clipped to the sector and with the side walls cut out so it
              does not interfere with them; homogenised steel+epoxy material ltcc_nose.

Each wall part is reconstructed cleanly (bolt holes removed, tilt respected) and the parts are merged into a
single closed surface; see `build_wall`. The placement of every mesh is authored in stls/cad__default.yaml and
uploaded by the gcad CAD feature (see ltcc.py). There are no per-sector copies at present.
"""

import os

import numpy as np
import pymeshlab as ml

from pygemc.utilities import cure_mesh, remove_holes

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = "/opt/projects/gemc/clas12Tags/geometry_source/ltcc/cad"
CADTMP = "/opt/projects/gemc/clas12Tags/geometry_source/ltcc/cadTempRemoved"
DST = os.path.join(HERE, "stls")

CONE_TARGET = 1500                      # facet cap for the Winston-cone mirrors

# Merged wall assemblies. Each part is (name, source_dir, reconstruction_mode):
#   "full" — flatten to a clean slab at the piece's full (thin) principal extent. Correct for genuinely
#            flat panels (S1-BW, S1-RW) and flat plates whose extent already is the material thickness.
#   "vol"  — flatten to a slab at the true average thickness (volume / footprint area). For *bent* thin
#            plates (S1-TB, S1-BB) whose principal extent spans well beyond the material and would
#            otherwise over-thicken them.
#   "cure" — keep the piece's real 3-D shape, only closing its open boundary (no flattening). For genuine
#            structural beams (S1-TRB, a thin-walled truss) that a slab/envelope would misrepresent.
# The parts overlap where they join, so merging (boolean union) removes the internal walls and yields one
# gap-free connected surface. All parts share the clas12Tags CAD coordinate frame, hence one placement each.
WALLS = {
    "backwall": {
        "parts": (("S1-BW", CADTMP, "full"), ("S1-TB", CAD, "vol"), ("S1-BB", CAD, "vol")),
        "fill": True,          # fill the hollow centre between the top and bottom bars into a solid plate
        "color": "ccccdd",
        "rotation": "180*deg, 0*deg, 60*deg",
    },
    "rightwall": {
        "parts": (("S1-RW", CADTMP, "full"), ("S1-BRB", CAD, "full"), ("S1-TRB", CADTMP, "cure")),
        "color": "ccddcc",     # S1-RW is already a full wall panel, so there is no central gap to fill
        "rotation": "180*deg, 0*deg, 60*deg",
    },
}

# Mirror-image walls: <name> is <source> reflected across the detector centre plane. The LTCC sector spans
# phi = 90..150 deg, so the centre line is phi = 120 deg; that plane contains the beam axis (z), and the
# walls' placement position sits on z, so the reflection commutes with the placement translation. The copy
# is reflected in its *own* frame (S = rot * M * rot^-1, rot the passive placement rotation) and therefore
# keeps the SAME placement (rotation + position) as its source. See `build_mirror_wall`.
CENTER_PHI = 120.0
MIRROR_WALLS = {
    "leftwall": {"source": "rightwall", "color": "ccddee"},
}

# The walls interpenetrate a few mm where they meet: the side panels against the backwall at the frame
# corners, and the two side panels against each other at the tent ridge (phi = 120). All walls share one
# placement, so this is resolved directly: each listed obstacle (dilated by WALL_CLEARANCE for a small gap)
# is boolean-subtracted from the wall. Done after the walls are built. rightwall also yields to leftwall at
# the ridge (one cut suffices to separate the pair). Order matters: leftwall is cut first so rightwall is
# then trimmed against the finalized leftwall.
WALL_OVERLAP_CUTS = {"leftwall": ("backwall",), "rightwall": ("backwall", "leftwall")}
WALL_CLEARANCE = 1.0                    # mm

# The nose: five support pieces approximated simply. Each part is (name, source_dir, mode):
#   "hull" — the compact head pieces are pooled and sliced along their long (PCA) axis at NOSE_SEG_EDGES
#            (finer toward the top), each slab convex-hulled; this gives the neck -> shoulder structure.
#   "flat" — NFrame is a big flat frame, so it is reconstructed as a single flat slab (flatten_pca, full
#            extent) rather than being chopped into the hull, which made a weird stepped shape there and
#            cut into its material.
# All the resulting solids are boolean-unioned into one nose. The pieces do not union cleanly raw and their
# internal structure is irrelevant. The result is larger than the parts' material volume, so ltcc_nose uses
# a mass-conserving density (see materials.py / stls/notes.md). All five parts come from clas12Tags (the
# nose bracket is the clas12Tags `Nose` mesh).
NOSE_PARTS = (
    ("Epoxy", CADTMP, "hull"), ("FrontPlate", CADTMP, "hull"), ("Mount", CADTMP, "hull"),
    ("Nose", CADTMP, "hull"), ("NFrame", CADTMP, "flat"),
)
# Segment boundaries as fractions along the long axis, bottom (0.0) -> top/neck (1.0); the segments are
# finer toward the top so the narrowing neck and shoulder get more structure than the plain body.
NOSE_SEG_EDGES = (0.0, 0.45, 0.68, 0.84, 1.0)
NOSE_SEG_OVERLAP = 0.12                # fraction of a mean segment length each slab overlaps its neighbours
NOSE_MATERIAL = "ltcc_nose"            # homogenised steel+epoxy mix, defined in materials.py
NOSE_COLOR = "cc8844"
# The nose CAD pieces sit one sector (60 deg) away from the wall pieces, so at the walls' rz = 60 deg they
# would land in sector 2; rz = 120 deg places the nose in sector 3 (phi 90..150, centred at 120) with the
# backwall/rightwall/leftwall.
NOSE_ROTATION = "180*deg, 0*deg, 120*deg"
NOSE_POSITION = (0.0, 0.0, 1273.7)     # mm, matches the YAML default position (on the beam axis)
# The convex/flat approximations bloat the nose past the sector edges, so it is clipped to this world phi
# wedge (deg) — a couple of degrees inside the phi = 90 / 150 side walls (the raw parts span only 93..147),
# so the nose cannot stick out through the left/right walls.
NOSE_SECTOR = (92.0, 148.0)
# The wall plates still have 3-D extent that reaches into the sector, so after clipping the nose also has
# these already-built volumes cut out of it (boolean difference = a slot where each plate passes through),
# guaranteeing the nose does not interfere with the walls or their plates/rails. (The backwall does not
# reach the nose, so it is not listed.)
NOSE_SUBTRACT = ("rightwall", "leftwall")
NOSE_CLEARANCE = 1.5                    # mm; the subtracted walls are dilated by this so the nose sits off
                                        # them with a real gap (Geant4 reports no overlap). The cut can
                                        # shave a small fragment off the nose; only the largest piece is kept.

# TEMPORARY comparison overlay: the raw parts (green) placed over the merged solid so it can be compared in
# the viewer. () for the clean final set; set to NOSE_PARTS (or a tuple of (name, source_dir)) to compare.
INDIVIDUALS = ()

# Winston cones: (name, segment, position, rotation). mother ltccS3, mirror ltcc_AlMgF2.
WINSTON = (
    ("WC_S", 1, "0.390826*cm, 58.2255*cm, 446.167*cm", "7.72*deg, -30.8*deg, 30.8*deg"),
    ("WC_M", 11, "76.6113*cm, 184.572*cm, 384.362*cm", "26.04*deg, -27.19*deg, 27.19*deg"),
    ("WC_L", 13, "93.0427*cm, 212.743*cm, 368.448*cm", "30.48*deg, -24*deg, 25.99*deg"),
)


def _hull2d(points):
    """2D convex hull (Andrew monotone chain), returning the outline vertices in CCW order."""
    ordered = np.array(sorted(map(tuple, points)))

    def turn(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in ordered:
        while len(lower) >= 2 and turn(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(tuple(p))
    upper = []
    for p in ordered[::-1]:
        while len(upper) >= 2 and turn(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(tuple(p))
    return np.array(lower[:-1] + upper[:-1])


def _extrude_hull(vertices, thickness=None):
    """Return (verts, faces) for the convex outline of `vertices` in their PCA thin plane, extruded
    through the thickness: the full principal extent if `thickness` is None, else a slab of that thickness
    centred on the mid-plane. The piece's tilt is respected (work is done in the principal frame)."""
    centre = vertices.mean(0)
    centred = vertices - centre
    _, _, axes = np.linalg.svd(centred, full_matrices=False)   # axes rows: largest -> smallest extent
    principal = centred @ axes.T
    thin, plane = 2, [0, 1]                                     # smallest principal extent is the thickness
    if thickness is None:
        top, bot = principal[:, thin].max(), principal[:, thin].min()
    else:
        top, bot = thickness / 2.0, -thickness / 2.0
    hull = _hull2d(principal[:, plane])
    n = len(hull)

    def point(u, v, w):
        p = [0.0, 0.0, 0.0]
        p[plane[0]], p[plane[1]], p[thin] = u, v, w
        return p

    local = np.array([point(u, v, top) for u, v in hull] + [point(u, v, bot) for u, v in hull])
    world = local @ axes + centre                              # back to world coordinates
    faces = []
    for i in range(1, n - 1):
        faces.append([0, i, i + 1])                            # top face (fan)
    for i in range(1, n - 1):
        faces.append([n, n + i + 1, n + i])                    # bottom face (fan)
    for i in range(n):
        a, b = i, (i + 1) % n
        faces += [[a, b, n + b], [a, n + b, n + i]]            # side walls
    return world, np.array(faces)


def flatten_pca(raw_path, thickness=None):
    """Clean flat slab of a single piece: its convex outline extruded through `thickness` (its full thin
    extent if None). Bolt holes vanish (outline only). A given `thickness` is used for *bent* plates whose
    full extent would over-thicken them. Returns (verts, faces)."""
    ms = ml.MeshSet()
    ms.load_new_mesh(raw_path)
    return _extrude_hull(ms.current_mesh().vertex_matrix(), thickness)


def _save_solid(verts, faces, out):
    """Coherently orient a (verts, faces) solid outward and save it."""
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(verts, faces))
    ms.meshing_re_orient_faces_coherently()
    if (ms.get_geometric_measures().get("mesh_volume") or 0) < 0:
        ms.meshing_invert_face_orientation()
    ms.save_current_mesh(out)


def _mesh_vertices(path):
    ms = ml.MeshSet()
    ms.load_new_mesh(path)
    return ms.current_mesh().vertex_matrix()


def _gap_filler(part_paths, out):
    """Solid plate that fills the hollow centre of an assembly: the convex outline of *all* its parts,
    extruded through the assembly's full thickness. Unioned with the parts it closes the gap between them
    (e.g. between the backwall's top and bottom bars) while leaving their outer envelope unchanged."""
    verts = np.vstack([_mesh_vertices(p) for p in part_paths])
    world, faces = _extrude_hull(verts, thickness=None)
    _save_solid(world, faces, out)


def _plate_thickness(raw_path):
    """True average thickness of a bent plate = its (de-holed) volume / footprint area."""
    tmp = os.path.join(DST, ".thickness_tmp.stl")
    cure_mesh(raw_path, tmp, target_faces=0, verbose=False)
    remove_holes(tmp, verbose=False)
    cure_mesh(tmp, target_faces=0, verbose=False)   # re-seal so the solid has a well-defined volume
    ms = ml.MeshSet()
    ms.load_new_mesh(tmp)
    volume = abs(ms.get_geometric_measures().get("mesh_volume"))
    vertices = ms.current_mesh().vertex_matrix()
    os.remove(tmp)
    centred = vertices - vertices.mean(0)
    _, _, axes = np.linalg.svd(centred, full_matrices=False)
    footprint = _hull2d((centred @ axes.T)[:, [0, 1]])
    x, y = footprint[:, 0], footprint[:, 1]
    area = 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
    return volume / area


def _part_solid(name, src, mode, out):
    """Write one clean, watertight part solid for the merge (see WALLS for the modes)."""
    raw = os.path.join(src, name + ".stl")
    if mode == "cure":                                          # keep the real 3-D shape, just close it
        cure_mesh(raw, out, target_faces=0, verbose=False)
        return
    thickness = _plate_thickness(raw) if mode == "vol" else None
    verts, faces = flatten_pca(raw, thickness)
    _save_solid(verts, faces, out)


def build_wall(wall, spec):
    """Combine a wall's parts into one watertight solid (stls/<wall>.stl). Each part is reconstructed as a
    clean slab (see WALLS) and the parts are boolean-unioned; where they overlap the internal walls vanish,
    leaving one gap-free connected surface.

    If the wall sets `fill`, the hollow centre between the parts (e.g. between the backwall's top and bottom
    bars) is filled instead: the full-extent `_gap_filler` plate already contains every part, so it *is* the
    merged solid — a single clean convex plate spanning the frame outline. Emitting it directly avoids the
    boolean union of the bars with their enclosing plate, which leaves coplanar / non-manifold artefacts."""
    parts = []
    for name, src, mode in spec["parts"]:
        parts.append(os.path.join(DST, f".{name}_slab.stl"))
        _part_solid(name, src, mode, parts[-1])
    out = os.path.join(DST, wall + ".stl")
    if spec.get("fill"):
        _gap_filler(parts, out)
    else:
        ms = ml.MeshSet()
        for part in parts:
            ms.load_new_mesh(part)
        ms.generate_boolean_union(first_mesh=0, second_mesh=1)
        for k in range(2, len(parts)):
            ms.generate_boolean_union(first_mesh=ms.mesh_number() - 1, second_mesh=k)
        ms.save_current_mesh(out)
    for part in parts:
        os.remove(part)
    report(out)


def _placement_rotation(rotation_str):
    """The passive-placement frame rotation matrix `rot` for a YAML rotation like "180*deg, 0*deg, 60*deg".
    GEMC applies rotateX, rotateY, rotateZ and CLHEP pre-multiplies, so rot = Rz * Ry * Rx."""
    angles = [np.deg2rad(float(tok.replace("*deg", "").strip())) for tok in rotation_str.split(",")]
    rx, ry, rz = angles

    def rot_x(a): return np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    def rot_y(a): return np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    def rot_z(a): return np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])

    return rot_z(rz) @ rot_y(ry) @ rot_x(rx)


def _mirror_in_local_frame(rotation_str, centre_phi):
    """Reflection matrix to apply to a mesh *in its own frame* so that, once placed with the given passive
    rotation, the placed copy is the world reflection across the phi = `centre_phi` plane (which contains z).
    Passive placement maps local -> world as world = rot^-1 * local + T, so with A = rot^-1 the world
    reflection M becomes S = A^-1 * M * A = rot * M * rot^-1 in the local frame."""
    rot = _placement_rotation(rotation_str)
    phi = np.deg2rad(centre_phi)
    c2, s2 = np.cos(2 * phi), np.sin(2 * phi)
    reflect = np.array([[c2, s2, 0], [s2, -c2, 0], [0, 0, 1]])   # reflection across the phi plane (∋ z)
    return rot @ reflect @ np.linalg.inv(rot)


def build_mirror_wall(name, spec):
    """Build stls/<name>.stl as the mirror image of another wall across the detector centre plane, reusing
    the source wall's placement. The reflection reverses the winding, so `_save_solid` re-orients it."""
    source = spec["source"]
    src_path = os.path.join(DST, source + ".stl")
    mirror = _mirror_in_local_frame(WALLS[source]["rotation"], CENTER_PHI)
    ms = ml.MeshSet()
    ms.load_new_mesh(src_path)
    verts = ms.current_mesh().vertex_matrix() @ mirror.T
    faces = ms.current_mesh().face_matrix()
    out = os.path.join(DST, name + ".stl")
    _save_solid(verts, faces, out)
    report(out)


def resolve_wall_overlaps():
    """Remove the frame-corner interpenetration between the walls: subtract each obstacle (dilated by
    WALL_CLEARANCE for a small gap) from its wall. The walls share one placement, so no transform is needed.
    Run after all walls are built, before the nose (which subtracts the finalized side walls)."""
    for wall, obstacles in WALL_OVERLAP_CUTS.items():
        target = os.path.join(DST, wall + ".stl")
        for obstacle in obstacles:
            source = ml.MeshSet()
            source.load_new_mesh(os.path.join(DST, obstacle + ".stl"))
            source.compute_normal_per_vertex()
            mesh = source.current_mesh()
            dilated = mesh.vertex_matrix() + mesh.vertex_normal_matrix() * WALL_CLEARANCE
            tmp = os.path.join(DST, f".{obstacle}_obstacle.stl")
            _save_solid(dilated, mesh.face_matrix(), tmp)
            ms = ml.MeshSet()
            ms.load_new_mesh(target)
            ms.load_new_mesh(tmp)
            ms.generate_boolean_difference(first_mesh=0, second_mesh=1)
            ms.save_current_mesh(target)
            os.remove(tmp)
        _keep_largest_component(target)
        report(target)


def _wall_rotation(name):
    """The placement rotation string of an already-built wall (in WALLS or MIRROR_WALLS)."""
    if name in WALLS:
        return WALLS[name]["rotation"]
    return WALLS[MIRROR_WALLS[name]["source"]]["rotation"]


def _subtract_obstacles(mesh_path):
    """Boolean-subtract the NOSE_SUBTRACT wall volumes from the mesh at `mesh_path`, so the nose has a slot
    wherever a wall plate passes through it and cannot interfere with the walls. Each wall is mapped from its
    own placement into the nose frame: with both placed at the same position, a wall-local point maps to the
    nose frame by M = rot_nose * rot_wall^-1 (the shared translation cancels)."""
    rot_nose = _placement_rotation(NOSE_ROTATION)
    for name in NOSE_SUBTRACT:
        transform = rot_nose @ np.linalg.inv(_placement_rotation(_wall_rotation(name)))
        wall = ml.MeshSet()
        wall.load_new_mesh(os.path.join(DST, name + ".stl"))
        wall.compute_normal_per_vertex()
        mesh = wall.current_mesh()
        dilated = mesh.vertex_matrix() + mesh.vertex_normal_matrix() * NOSE_CLEARANCE  # small clearance
        verts = dilated @ transform.T
        faces = mesh.face_matrix()
        tmp = os.path.join(DST, f".{name}_obstacle.stl")
        _save_solid(verts, faces, tmp)
        ms = ml.MeshSet()
        ms.load_new_mesh(mesh_path)
        ms.load_new_mesh(tmp)
        ms.generate_boolean_difference(first_mesh=0, second_mesh=1)
        ms.save_current_mesh(mesh_path)
        os.remove(tmp)
    _keep_largest_component(mesh_path)


def _keep_largest_component(mesh_path):
    """Keep only the largest connected component of the mesh (drops small fragments a wall cut may shave off
    the nose), leaving one clean watertight solid."""
    ms = ml.MeshSet()
    ms.load_new_mesh(mesh_path)
    ms.generate_splitting_by_connected_components()
    best, best_volume = None, -1.0
    for i in range(1, ms.mesh_number()):                          # 0 is the original; 1.. are components
        ms.set_current_mesh(i)
        if ms.current_mesh().face_number() == 0:
            continue
        volume = abs(ms.get_geometric_measures().get("mesh_volume") or 0)
        if volume > best_volume:
            best, best_volume = i, volume
    ms.set_current_mesh(best)
    ms.save_current_mesh(mesh_path)


def _clip_to_sector(mesh_path):
    """Clip the mesh at `mesh_path` (in the nose's own frame) to the world phi wedge NOSE_SECTOR so it stays
    inside the sector and cannot cross the phi = 90 / 150 side walls. The wedge (a triangular prism through
    the beam axis) is built in world coordinates and mapped into the mesh frame via the passive placement
    (local = rot * (world - position)), then boolean-intersected with the mesh."""
    rot = _placement_rotation(NOSE_ROTATION)
    origin = np.array(NOSE_POSITION)
    phi_lo, phi_hi = np.deg2rad(NOSE_SECTOR[0]), np.deg2rad(NOSE_SECTOR[1])
    radius, z_lo, z_hi = 1500.0, 4000.0, 8000.0
    world = []
    for z in (z_lo, z_hi):
        world.append([0.0, 0.0, z])
        world.append([radius * np.cos(phi_lo), radius * np.sin(phi_lo), z])
        world.append([radius * np.cos(phi_hi), radius * np.sin(phi_hi), z])
    local = (rot @ (np.array(world) - origin).T).T
    wedge = ml.MeshSet()
    wedge.add_mesh(ml.Mesh(local))
    wedge.generate_convex_hull()
    tmp = os.path.join(DST, ".sector_wedge.stl")
    wedge.save_current_mesh(tmp)
    ms = ml.MeshSet()
    ms.load_new_mesh(mesh_path)
    ms.load_new_mesh(tmp)
    ms.generate_boolean_intersection(first_mesh=0, second_mesh=1)
    ms.save_current_mesh(mesh_path)
    os.remove(tmp)


def build_nose():
    """Approximate the five nose pieces by a few simple solids unioned into one (stls/nose.stl). The "hull"
    (head) pieces are cured, pooled, sliced into overlapping segments along their long (PCA) axis (boundaries
    NOSE_SEG_EDGES, finer toward the top) and each segment convex-hulled -> the neck/shoulder structure. Each
    "flat" piece (NFrame) is reconstructed as a single flat slab (flatten_pca, full extent). All solids are
    boolean-unioned. See NOSE_* and stls/notes.md."""
    hull_points = []
    flat_slabs = []
    for name, src, mode in NOSE_PARTS:
        cured = os.path.join(DST, f".{name}_cure.stl")
        cure_mesh(os.path.join(src, name + ".stl"), cured, target_faces=0, verbose=False)
        if mode == "flat":
            slab = os.path.join(DST, f".{name}_flat.stl")
            verts, faces = flatten_pca(cured)                        # full-extent flat slab
            _save_solid(verts, faces, slab)
            flat_slabs.append(slab)
        else:
            hull_points.append(_mesh_vertices(cured))
        os.remove(cured)

    points = np.vstack(hull_points)
    _, _, axes = np.linalg.svd(points - points.mean(0), full_matrices=False)
    long_axis = ((points - points.mean(0)) @ axes.T)[:, 0]           # largest-extent coordinate
    # The PCA axis sign is arbitrary; orient it so long_axis increases toward the top (higher world z),
    # keeping the finer NOSE_SEG_EDGES at the neck rather than the tail.
    if points[long_axis.argmax(), 2] < points[long_axis.argmin(), 2]:
        long_axis = -long_axis
    lo, hi = long_axis.min(), long_axis.max()
    edges = lo + np.array(NOSE_SEG_EDGES) * (hi - lo)
    span = (hi - lo) * NOSE_SEG_OVERLAP / (len(NOSE_SEG_EDGES) - 1)

    ms = ml.MeshSet()
    for i in range(len(NOSE_SEG_EDGES) - 1):
        selected = (long_axis >= edges[i] - span) & (long_axis <= edges[i + 1] + span)
        if selected.sum() < 10:
            continue
        seg = ml.MeshSet()
        seg.add_mesh(ml.Mesh(points[selected]))                      # point cloud of this slab
        seg.generate_convex_hull()
        tmp = os.path.join(DST, f".nose_seg{i}.stl")
        seg.save_current_mesh(tmp)
        ms.load_new_mesh(tmp)
        os.remove(tmp)
    for slab in flat_slabs:
        ms.load_new_mesh(slab)
        os.remove(slab)

    inputs = ms.mesh_number()                                        # capture before unions add meshes
    ms.generate_boolean_union(first_mesh=0, second_mesh=1)
    for k in range(2, inputs):
        ms.generate_boolean_union(first_mesh=ms.mesh_number() - 1, second_mesh=k)
    out = os.path.join(DST, "nose.stl")
    ms.save_current_mesh(out)
    _clip_to_sector(out)                                          # keep the nose inside the sector
    _subtract_obstacles(out)                                      # cut slots so it clears the wall plates
    report(out)


def build_cones():
    for name, *_ in WINSTON:
        out = os.path.join(DST, name + ".stl")
        cure_mesh(os.path.join(CAD, name + ".stl"), out, target_faces=CONE_TARGET, verbose=False)
        report(out)


def build_individuals():
    """TEMPORARY (comparison): copy the raw parts into stls/ unchanged (skip any already sourced there)."""
    import shutil
    for name, src, *_ in INDIVIDUALS:
        dst = os.path.join(DST, name + ".stl")
        source = os.path.join(src, name + ".stl")
        if os.path.abspath(source) != os.path.abspath(dst):
            shutil.copy(source, dst)
        report(dst)


def report(path):
    ms = ml.MeshSet()
    ms.load_new_mesh(path)
    ms.compute_selection_by_non_manifold_edges_per_face()
    nm = ms.current_mesh().selected_face_number()
    ms.set_selection_none()
    topo = ms.get_topological_measures()
    print(f"  {os.path.basename(path):14s} F={ms.current_mesh().face_number():5d} "
          f"genus={topo.get('genus'):>3} bnd={topo.get('boundary_edges')} "
          f"CC={topo.get('connected_components_number')} nonmanifold={nm}")


def emit_yaml(path):
    lines = [
        "# LTCC CAD placement for GEMC3's gcad CAD factory (see ../../../../src/examples/basic/cad).",
        "# Generated once by `build_cad_meshes.py --yaml`; after that this file is the source of truth.",
        "# To resolve a Geant4 volume overlap, nudge the offending volume's `position` by a few mm.",
        "",
        "system:     stls",
        "experiment: clas12",
        "variation:  default",
        "cad_dir:    stls",
        "extension:  stl",
        "",
        "defaults:",
        "  position:         0*mm, 0*mm, 1273.7*mm",
        "  g4placement_type: passive",
        "  style:            1",
        "",
        "volumes:",
    ]

    def vol(**kw):
        lines.append(f"  - name: {kw.pop('name')}")
        for key, value in kw.items():
            lines.append(f"    {key}: {value}")

    for name, segment, position, rotation in WINSTON:
        vol(name=name, mother="ltccS3", material="ltcc_WC_material", color="aa9999",
            mirror="ltcc_AlMgF2", identifier=f'"sector: 1, side: 2, segment: {segment}"',
            position=position, rotation=rotation)
    # merged sector-3 frame assemblies, each placed like the sector-3 frame.
    for wall, spec in WALLS.items():
        vol(name=wall, material="G4_Al", color=spec["color"], rotation=spec["rotation"])
    # mirror-image walls: reflected mesh, same placement as their source wall.
    for wall, spec in MIRROR_WALLS.items():
        vol(name=wall, material="G4_Al", color=spec["color"], rotation=WALLS[spec["source"]]["rotation"])
    # nose: single filled solid of the five support pieces, homogenised steel+epoxy material, in sector 3.
    vol(name="nose", material=NOSE_MATERIAL, color=NOSE_COLOR, rotation=NOSE_ROTATION)
    # TEMPORARY (comparison): the raw nose parts, green, same placement so they overlay the nose.
    for name, *_ in INDIVIDUALS:
        vol(name=name, material="G4_Al", color="00ee00", rotation=NOSE_ROTATION)

    with open(path, "w") as stream:
        stream.write("\n".join(lines) + "\n")
    print(f"  wrote {path} ({sum(1 for l in lines if l.startswith('  - name'))} volumes)")


def main():
    os.makedirs(DST, exist_ok=True)
    build_cones()
    for wall, spec in WALLS.items():
        build_wall(wall, spec)
    for wall, spec in MIRROR_WALLS.items():
        build_mirror_wall(wall, spec)   # mirror of an already-built wall (see MIRROR_WALLS)
    resolve_wall_overlaps()             # clear the backwall/side-wall corner interpenetration
    build_nose()
    build_individuals()   # TEMPORARY: raw parts for comparison (see INDIVIDUALS)


if __name__ == "__main__":
    import sys
    if "--yaml" in sys.argv:
        emit_yaml(os.path.join(DST, "cad__default.yaml"))
    else:
        main()
