#!/usr/bin/env python3
"""Regenerate the HTCC CAD meshes in stls/ from the clas12Tags sources.

    <gemc-dev python_env>/python3 build_cad_meshes.py          # rebuild the STL meshes
    <gemc-dev python_env>/python3 build_cad_meshes.py --report # only print topology of stls/

Needs pymeshlab, so run it with the gemc-dev python environment (the same one that has pygemc):

    /opt/jlab_software/<platform>/gemc/dev/python_env/bin/python3 build_cad_meshes.py

Rebuild from archived engineering inputs, never from the already processed active meshes. The entry cone
and extension use the existing curing recipe. The Moller cone uses a dedicated union of its engineering
cone and collar, resolving the internal seam while retaining its bore and bounds. No Poisson reconstruction
or engineering-hole filling is used. Placement is authored per variation in geometry.py (`build_cad`).
"""

import argparse
import os
from pathlib import Path

import pymeshlab as ml

from pygemc.utilities import cure_mesh
from repair_moller_cone import repair

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = "/opt/projects/gemc/clas12Tags/geometry_source/htcc/cad_original"
DST = os.path.join(HERE, "stls")

# name: (target_faces, remove_self_intersections). target_faces=0 keeps the source resolution.
MESHES = {
    "htccCone": (6000, False),          # double-walled entry cone, decimated from 18818 facets
    "htccMollerCone": (0, False),      # dedicated engineering cone/collar union, preserving the bore
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


def build(source=CAD, output=DST, names=None):
    os.makedirs(output, exist_ok=True)
    for name in names or MESHES:
        target_faces, remove_self_intersections = MESHES[name]
        out = os.path.join(output, name + ".stl")
        if name == "htccMollerCone":
            repair(Path(source) / (name + ".stl"), Path(out))
            report(out)
            continue
        cure_mesh(
            os.path.join(source, name + ".stl"), out,
            target_faces=target_faces,
            remove_self_intersections=remove_self_intersections,
            verbose=False,
        )
        report(out)


def report_only(output=DST, names=None):
    for name in names or MESHES:
        report(os.path.join(output, name + ".stl"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--source", type=Path, default=Path(CAD))
    parser.add_argument("--output", type=Path, default=Path(DST))
    parser.add_argument("--mesh", action="append", choices=MESHES)
    args = parser.parse_args()
    if args.report:
        report_only(args.output, args.mesh)
    else:
        build(args.source, args.output, args.mesh)
