#!/usr/bin/env python3
"""Verify that the three existing bore meshes are minimal for their unchanged annular rims."""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pymeshlab as ml


NAMES = {"BoreShield": "BoreShield", "CenterTube": "BoreCenterTube", "WarmBoreTube": "WarmBoreTube"}


def audit(originals, active, output):
    report = {}
    for source, name in NAMES.items():
        original = originals / f"{source}.stl"
        target = active / f"{name}.stl"
        assert original.read_bytes() == target.read_bytes(), name
        meshes = ml.MeshSet()
        meshes.load_new_mesh(str(target))
        vertices = meshes.current_mesh().vertex_matrix()
        faces = meshes.current_mesh().face_matrix()
        topology = meshes.get_topological_measures()
        assert topology["is_mesh_two_manifold"] and topology["boundary_edges"] == 0
        assert topology["genus"] == topology["connected_components_number"] == 1
        assert len(faces) == 2 * len(vertices)
        assert len(np.unique(vertices[:, 2])) == 2
        triangles = vertices[faces]
        areas = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                       triangles[:, 2] - triangles[:, 0]), axis=1) / 2
        assert np.all(areas > 0), name
        edges = np.vstack((faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]))
        directed = {tuple(edge) for edge in edges}
        assert len(directed) == len(edges) and all((b, a) in directed for a, b in edges), name
        radius = np.linalg.norm(vertices[:, :2], axis=1)
        rings = []
        for z in np.unique(vertices[:, 2]):
            for inner in (True, False):
                indices = np.flatnonzero((vertices[:, 2] == z) &
                                         ((radius < (radius.min() + radius.max()) / 2) == inner))
                points = vertices[indices, :2]
                angles = np.arctan2(points[:, 1], points[:, 0])
                points = points[np.argsort(angles)]
                u = points - np.roll(points, 1, axis=0)
                v = np.roll(points, -1, axis=0) - points
                turns = u[:, 0] * v[:, 1] - u[:, 1] * v[:, 0]
                assert np.all(turns > 0), name
                rings.append({"z_mm": float(z), "inner": inner, "corners": len(indices),
                              "min_turn_cross_mm2": float(turns.min())})
        meshes.compute_selection_by_self_intersections_per_face()
        assert meshes.current_mesh().selected_face_number() == 0
        report[name] = {"source": original.name, "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
                        "vertices": len(vertices), "facets_before": len(faces), "facets_after": len(faces),
                        "facet_reduction_percent": 0.0, "bytes_unchanged": True, "rings": rings,
                        "topology": topology, "self_intersecting_faces": 0,
                        "degenerate_faces": 0, "coherently_oriented": True,
                        "volume_mm3": meshes.get_geometric_measures()["mesh_volume"],
                        "minimal_for_existing_rim_corners": True, "all_holes_unchanged": True}
    output.write_text(json.dumps(report, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originals", type=Path, required=True)
    parser.add_argument("--active", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    audit(args.originals, args.active, args.output)


if __name__ == "__main__":
    main()
