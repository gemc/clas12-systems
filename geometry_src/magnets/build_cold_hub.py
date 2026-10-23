#!/usr/bin/env python3
"""Repair and simplify ColdHub while retaining every opening and the engineering coordinates."""

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab as ml


SOURCE_SHA256 = "5e416560fae19d674de72f83af6379b27325091896df736723aae809ef7db63f"


def load(path):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(path))
    return meshes


def surface_stats(meshes):
    vertices = meshes.current_mesh().vertex_matrix()
    faces = meshes.current_mesh().face_matrix()
    triangles = vertices[faces]
    area = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                   triangles[:, 2] - triangles[:, 0]), axis=1) / 2
    meshes.compute_selection_by_self_intersections_per_face()
    return {"vertices": len(vertices), "facets": len(faces), "topology": meshes.get_topological_measures(),
            "self_intersecting_faces": meshes.current_mesh().selected_face_number(),
            "degenerate_faces": int((area < 1e-10).sum()),
            "bounds_mm": [vertices.min(0).tolist(), vertices.max(0).tolist()]}


def repair(vertices, faces):
    """Close two triangular export slivers and retriangulate seven collinear T-junctions."""
    edges = {}
    for face in faces:
        for a, b in zip(face, np.roll(face, -1)):
            edges.setdefault(tuple(sorted((int(a), int(b)))), []).append((int(a), int(b)))
    boundary = {edge for edge, around in edges.items() if len(around) == 1}
    assert len(boundary) == 6
    vertices_at_seam = sorted({a for edge in boundary for a in edge})
    patches = []
    for a, b, c in itertools.combinations(vertices_at_seam, 3):
        if not {(a, b), (a, c), (b, c)} <= boundary:
            continue
        if (a, b) in edges[(a, b)]:
            a, b = b, a
        patches.append([a, b, c])
    assert len(patches) == 2
    patch_points = vertices[np.array(patches)]
    patch_areas = np.linalg.norm(np.cross(patch_points[:, 1] - patch_points[:, 0],
                                         patch_points[:, 2] - patch_points[:, 0]), axis=1) / 2
    assert max(patch_areas) < 0.01  # Export slivers, not drilled openings.
    meshes = ml.MeshSet()
    meshes.add_mesh(ml.Mesh(vertices, np.vstack((faces, patches))))
    before_orientation = meshes.current_mesh().face_matrix().copy()
    meshes.meshing_re_orient_faces_coherently()
    repaired = meshes.current_mesh().face_matrix().copy()
    reoriented = int(np.any(repaired != before_orientation, axis=1).sum())
    junctions = 0
    for _ in range(20):
        triangles = vertices[repaired]
        areas = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                        triangles[:, 2] - triangles[:, 0]), axis=1) / 2
        bad = np.flatnonzero(areas < 1e-10)
        if not len(bad):
            break
        index = int(bad[0])
        face = repaired[index]
        _, a, b = max((np.linalg.norm(vertices[a] - vertices[b]), int(a), int(b))
                      for a, b in zip(face, np.roll(face, -1)))
        middle = next(int(x) for x in face if x not in (a, b))
        other = [j for j, triangle in enumerate(repaired) if j != index and a in triangle and b in triangle]
        assert len(other) == 1
        j = other[0]
        triangle = repaired[j].copy()
        k = next(k for k in range(3) if {int(triangle[k]), int(triangle[(k + 1) % 3])} == {a, b})
        u, w, opposite = (int(triangle[k]), int(triangle[(k + 1) % 3]), int(triangle[(k + 2) % 3]))
        assert not any(middle in t and opposite in t for t in repaired)
        repaired[index] = [u, middle, opposite]
        repaired[j] = [middle, w, opposite]
        junctions += 1
    assert junctions == 7
    return repaired, {"seam_patch_areas_mm2": patch_areas.tolist(),
                      "seam_patch_vertices_mm": patch_points.tolist(),
                      "reoriented_faces": reoriented, "retriangulated_junctions": junctions}


def simplify(vertices, faces):
    """Collapse only edges satisfying the manifold link condition and a 0.0001 mm plane bound."""
    faces = faces.copy()
    active = np.ones(len(faces), dtype=bool)
    adjacent = [set() for _ in vertices]
    for i, triangle in enumerate(faces):
        for point in triangle:
            adjacent[point].add(i)
    collapsed = []
    for _ in range(8):
        count = 0
        for a in range(len(vertices)):
            star = adjacent[a]
            if not star:
                continue
            neighbors = {int(x) for i in star for x in faces[i]} - {a}
            for b in sorted(neighbors, key=lambda b: (float(np.linalg.norm(vertices[a] - vertices[b])), b)):
                common = star & adjacent[b]
                if len(common) != 2:
                    continue
                other_neighbors = {int(x) for i in adjacent[b] for x in faces[i]} - {b}
                opposite = {int(x) for i in common for x in faces[i]} - {a, b}
                if neighbors & other_neighbors != opposite:
                    continue
                valid, error = True, 0.0
                for i in sorted(star - common):
                    old = vertices[faces[i]]
                    new = vertices[np.where(faces[i] == a, b, faces[i])]
                    normal = np.cross(old[1] - old[0], old[2] - old[0])
                    length = np.linalg.norm(normal)
                    changed = np.cross(new[1] - new[0], new[2] - new[0])
                    deviation = abs(np.dot(vertices[b] - old[0], normal)) / length
                    if deviation > 1e-4 or np.linalg.norm(changed) < 1e-9 or np.dot(normal, changed) <= 0:
                        valid = False
                        break
                    error = max(error, float(deviation))
                if not valid:
                    continue
                for i in sorted(star):
                    for point in faces[i]:
                        adjacent[point].discard(i)
                    if i in common:
                        active[i] = False
                    else:
                        faces[i] = np.where(faces[i] == a, b, faces[i])
                        for point in faces[i]:
                            adjacent[point].add(i)
                collapsed.append({"removed_vertex_mm": vertices[a].tolist(),
                                  "retained_vertex_mm": vertices[b].tolist(), "plane_error_mm": error})
                count += 1
                break
        if not count:
            break
    return faces[active], collapsed


def build(source, output, catalogs):
    path = source / "Hub001.stl"
    original = load(path)
    vertices = original.current_mesh().vertex_matrix()
    faces = original.current_mesh().face_matrix()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == SOURCE_SHA256
    before = surface_stats(original)
    repaired, repairs = repair(vertices, faces)
    reference = ml.MeshSet()
    reference.add_mesh(ml.Mesh(vertices, repaired))
    reference_stats = surface_stats(reference)
    reduced, collapsed = simplify(vertices, repaired)
    meshes = ml.MeshSet()
    meshes.add_mesh(ml.Mesh(vertices, reduced))
    meshes.meshing_remove_unreferenced_vertices()
    target = output / "ColdHub.stl"
    meshes.save_current_mesh(str(target), binary=True)
    stored = load(target)
    after = surface_stats(stored)
    topology = after["topology"]
    assert topology["boundary_edges"] == 0 and topology["is_mesh_two_manifold"]
    assert topology["genus"] == reference_stats["topology"]["genus"] == 34
    assert topology["connected_components_number"] == 1
    assert after["self_intersecting_faces"] == after["degenerate_faces"] == 0
    assert before["bounds_mm"] == after["bounds_mm"]
    reference_volume = reference.get_geometric_measures()["mesh_volume"]
    volume = stored.get_geometric_measures()["mesh_volume"]
    assert abs(volume / reference_volume - 1) < 1e-9
    report = {"source_sha256": SOURCE_SHA256, "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
              "before": before, "closed_reference": reference_stats, "after": after, "repairs": repairs,
              "collapsed_edges": collapsed, "all_holes_retained": True, "bounds_unchanged": True,
              "max_local_plane_error_mm": max(row["plane_error_mm"] for row in collapsed),
              "closed_reference_volume_mm3": reference_volume, "optimized_volume_mm3": volume,
              "volume_change_percent": 100 * (volume / reference_volume - 1)}
    (output / "cold_hub_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    if catalogs:
        destination = output / "catalog"
        destination.mkdir(exist_ok=True)
        for path in sorted(catalogs.glob("cad_*.gxml")):
            root = ET.parse(path).getroot()
            for row in root:
                if row.get("name") in ("Hub001", "ColdHub"):
                    row.set("name", "ColdHub")
                    row.set("position", "0.000*mm 0.000*mm 1273.270*mm")
            lines = ["<gxml>"]
            for row in root:
                attrs = list(row.attrib.items())
                lines.append(f'  <volume {attrs[0][0]}="{attrs[0][1]}"')
                lines.extend(f'          {key}="{value}"' for key, value in attrs[1:-1])
                key, value = attrs[-1]
                lines.append(f'          {key}="{value}"/>')
            (destination / path.name).write_text("\n".join([*lines, "</gxml>"]) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--catalogs", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    build(args.source, args.output, args.catalogs)


if __name__ == "__main__":
    main()
