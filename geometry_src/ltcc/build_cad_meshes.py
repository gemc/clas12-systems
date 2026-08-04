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

# TEMPORARY: the raw parts of the wall currently being validated, copied verbatim (unchanged, holes and all)
# as separate volumes (green) so the merged solid can be compared against the originals in the viewer. They
# overlay the merged wall (same placement). Empty the list (and delete the copied stls) when done comparing.
INDIVIDUALS = (("S1-RW", CADTMP), ("S1-BRB", CAD), ("S1-TRB", CADTMP))

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


def build_cones():
    for name, *_ in WINSTON:
        out = os.path.join(DST, name + ".stl")
        cure_mesh(os.path.join(CAD, name + ".stl"), out, target_faces=CONE_TARGET, verbose=False)
        report(out)


def build_individuals():
    """TEMPORARY (comparison): copy the raw wall parts from clas12Tags into stls/ unchanged."""
    import shutil
    for name, src in INDIVIDUALS:
        shutil.copy(os.path.join(src, name + ".stl"), os.path.join(DST, name + ".stl"))
        report(os.path.join(DST, name + ".stl"))


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
    # TEMPORARY (comparison): the raw parts, green, same placement so they overlay the merged wall.
    for name, _src in INDIVIDUALS:
        vol(name=name, material="G4_Al", color="00ee00", rotation="180*deg, 0*deg, 60*deg")

    with open(path, "w") as stream:
        stream.write("\n".join(lines) + "\n")
    print(f"  wrote {path} ({sum(1 for l in lines if l.startswith('  - name'))} volumes)")


def main():
    os.makedirs(DST, exist_ok=True)
    build_cones()
    for wall, spec in WALLS.items():
        build_wall(wall, spec)
    build_individuals()   # TEMPORARY: raw parts for comparison (see INDIVIDUALS)


if __name__ == "__main__":
    import sys
    if "--yaml" in sys.argv:
        emit_yaml(os.path.join(DST, "cad__default.yaml"))
    else:
        main()
