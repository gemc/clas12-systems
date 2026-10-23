#!/usr/bin/env python3
"""Union the engineering cone and collar without capping the bore or reconstructing their surfaces."""

from collections import defaultdict
import hashlib
import json
from pathlib import Path
import tempfile

import numpy as np
import pymeshlab as ml


SOURCE_SHA256 = "6101a733fa5928cfa83f14b83b0d44c92c548ce44e505f5aa6d60c87be4d63d1"
SEAM_OFFSET_MM = 0.0001
WELD_DISTANCE_MM = 0.0002


def load(path):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(path))
    return meshes


def stats(meshes):
    vertices = meshes.current_mesh().vertex_matrix()
    faces = meshes.current_mesh().face_matrix()
    triangles = vertices[faces]
    areas = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                   triangles[:, 2] - triangles[:, 0]), axis=1) / 2
    meshes.compute_selection_by_self_intersections_per_face()
    return {"vertices": len(vertices), "facets": len(faces), "topology": meshes.get_topological_measures(),
            "degenerate_faces": int((areas == 0).sum()),
            "self_intersecting_faces": meshes.current_mesh().selected_face_number(),
            "bounds_mm": [vertices.min(0).tolist(), vertices.max(0).tolist()],
            "volume_mm3": meshes.get_geometric_measures().get("mesh_volume")}


def canonical_order(meshes):
    """Keep Boolean output ordering independent of the kernel's face traversal order."""
    vertices = meshes.current_mesh().vertex_matrix()
    faces = meshes.current_mesh().face_matrix()
    order = np.lexsort(vertices.T[::-1])
    remap = np.empty(len(order), dtype=int)
    remap[order] = np.arange(len(order))
    faces = remap[faces]
    faces = np.array([np.roll(face, -int(np.argmin(face))) for face in faces])
    result = ml.MeshSet()
    result.add_mesh(ml.Mesh(vertices[order], faces[np.lexsort(faces.T[::-1])]))
    return result


def engineering_parts(faces):
    """Separate two closed shells at the 45 edges shared by four engineering facets."""
    edges = defaultdict(list)
    for index, face in enumerate(faces):
        for a, b in zip(face, np.roll(face, -1)):
            edges[tuple(sorted((int(a), int(b))))].append(index)
    contact = [edge for edge, around in edges.items() if len(around) == 4]
    assert len(contact) == 45 and all(len(around) in (2, 4) for around in edges.values())
    adjacent = [set() for _ in faces]
    for around in edges.values():
        if len(around) == 2:
            a, b = around
            adjacent[a].add(b)
            adjacent[b].add(a)
    seen, parts = set(), []
    for index in range(len(faces)):
        if index in seen:
            continue
        pending, component = [index], []
        seen.add(index)
        while pending:
            current = pending.pop()
            component.append(current)
            for neighbor in sorted(adjacent[current]):
                if neighbor not in seen:
                    pending.append(neighbor)
                    seen.add(neighbor)
        parts.append(np.array(sorted(component)))
    parts.sort(key=len, reverse=True)
    assert [len(part) for part in parts] == [5688, 544]
    return parts, np.unique(np.array(contact))


def repair(source, target):
    source, target = Path(source), Path(target)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == SOURCE_SHA256
    original = load(source)
    before = stats(original)
    vertices = original.current_mesh().vertex_matrix()
    faces = original.current_mesh().face_matrix()
    parts, contact = engineering_parts(faces)
    assert len(contact) == 45 and len(np.unique(vertices[contact, 2])) == 1
    meshes, volumes = ml.MeshSet(), []
    for index, part in enumerate(parts):
        points = vertices.copy()
        if index == 1:
            # Resolve a zero-width four-face seam before exact Boolean union. The outer bounds stay fixed.
            radial = points[contact, :2] - [0.0, 0.00409205537289381]
            points[contact, :2] -= SEAM_OFFSET_MM * radial / np.linalg.norm(radial, axis=1)[:, None]
        meshes.add_mesh(ml.Mesh(points, faces[part]))
        meshes.meshing_remove_unreferenced_vertices()
        topology = meshes.get_topological_measures()
        assert topology["is_mesh_two_manifold"] and topology["boundary_edges"] == 0
        assert topology["genus"] == 1
        volumes.append(meshes.get_geometric_measures()["mesh_volume"])
    meshes.generate_boolean_union(first_mesh=0, second_mesh=1)
    meshes.meshing_remove_duplicate_vertices()
    meshes.meshing_remove_duplicate_faces()
    meshes.meshing_remove_null_faces()
    meshes.meshing_remove_unreferenced_vertices()
    union_volume = meshes.get_geometric_measures()["mesh_volume"]
    with tempfile.TemporaryDirectory(prefix="htcc-moller-") as directory:
        quantized = Path(directory) / "union.stl"
        meshes.save_current_mesh(str(quantized), binary=True)
        meshes = load(quantized)
    # Boolean intersection vertices can coincide after binary-STL float32 rounding. Weld only that scale.
    meshes.meshing_merge_close_vertices(threshold=ml.PureValue(WELD_DISTANCE_MM))
    meshes.meshing_remove_duplicate_faces()
    meshes.meshing_remove_null_faces()
    meshes.meshing_remove_unreferenced_vertices()
    meshes.meshing_re_orient_faces_coherently()
    if meshes.get_geometric_measures()["mesh_volume"] < 0:
        meshes.meshing_invert_face_orientation()
    meshes = canonical_order(meshes)
    target.parent.mkdir(parents=True, exist_ok=True)
    meshes.save_current_mesh(str(target), binary=True)
    stored = load(target)
    after = stats(stored)
    topology = after["topology"]
    assert topology["is_mesh_two_manifold"] and topology["boundary_edges"] == 0
    assert topology["genus"] == topology["connected_components_number"] == 1
    assert after["degenerate_faces"] == after["self_intersecting_faces"] == 0
    assert after["bounds_mm"] == before["bounds_mm"]
    assert abs(after["volume_mm3"] / union_volume - 1) < 1e-7
    report = {"source_sha256": SOURCE_SHA256,
              "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
              "before": before, "after": after, "engineering_part_facets": [len(p) for p in parts],
              "seam_vertices": len(contact), "seam_offset_mm": SEAM_OFFSET_MM,
              "stl_weld_distance_mm": WELD_DISTANCE_MM,
              "adjusted_part_volumes_mm3": [round(volume, 8) for volume in volumes],
              "union_before_stl_volume_mm3": round(union_volume, 8),
              "stl_volume_change_percent": round(100 * (after["volume_mm3"] / union_volume - 1), 12),
              "bounds_unchanged": True, "bore_retained": True, "reconstruction": False}
    (target.parent / "moller_cone_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    return report
