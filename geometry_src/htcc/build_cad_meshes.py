#!/usr/bin/env python3
"""Regenerate the HTCC CAD meshes in stls/ from the clas12Tags sources.

    <gemc-dev python_env>/python3 build_cad_meshes.py          # rebuild the STL meshes
    <gemc-dev python_env>/python3 build_cad_meshes.py --report # only print topology of stls/

Needs pymeshlab, so run it with the gemc-dev python environment (the same one that has pygemc):

    /opt/jlab_software/<platform>/gemc/dev/python_env/bin/python3 build_cad_meshes.py

The three HTCC beamline cones (the entry cone and the two Moller cones) are loaded by GEMC2 as raw
CADMesh tessellated solids. Here each is cured into a watertight, coherently oriented, decimated
G4-ready solid: vertices merged, open boundaries closed, normals made outward, and (for htccMollerCone)
self-intersections removed. The cones keep their real shape — no hole filling and no reconstruction — so
the double-walled htccCone/htccMollerConeExt keep both shells. Placement is authored per variation in
geometry.py (`build_cad`); there are no per-copy placements.
"""

import os
import sys

import pymeshlab as ml

from pygemc.utilities import cure_mesh

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = "/opt/projects/gemc/clas12Tags/geometry_source/htcc/cad"
DST = os.path.join(HERE, "stls")

# name: (target_faces, remove_self_intersections). target_faces=0 keeps the source resolution.
MESHES = {
    "htccCone": (6000, False),          # double-walled entry cone, decimated from 18818 facets
    "htccMollerCone": (6000, True),     # single-shell Moller cone; needs self-intersection removal
    "htccMollerConeExt": (0, False),    # small double-walled extension, already light (1748 facets)
}


def report(path):
    ms = ml.MeshSet()
    ms.load_new_mesh(path)
    ms.compute_selection_by_non_manifold_edges_per_face()
    nm = ms.current_mesh().selected_face_number()
    ms.set_selection_none()
    topo = ms.get_topological_measures()
    print(f"  {os.path.basename(path):20s} F={ms.current_mesh().face_number():6d} "
          f"genus={topo.get('genus')!s:>4} bnd={topo.get('boundary_edges')} "
          f"CC={topo.get('connected_components_number')} nonmanifold={nm}")


def build():
    os.makedirs(DST, exist_ok=True)
    for name, (target_faces, remove_self_intersections) in MESHES.items():
        out = os.path.join(DST, name + ".stl")
        cure_mesh(
            os.path.join(CAD, name + ".stl"), out,
            target_faces=target_faces,
            remove_self_intersections=remove_self_intersections,
            verbose=False,
        )
        report(out)


def report_only():
    for name in MESHES:
        report(os.path.join(DST, name + ".stl"))


if __name__ == "__main__":
    if "--report" in sys.argv:
        report_only()
    else:
        build()
