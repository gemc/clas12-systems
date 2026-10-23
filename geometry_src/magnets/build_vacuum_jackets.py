#!/usr/bin/env python3
"""Simplify jacket borders while preserving every hole surface and distinct export details.

Run with the mesh-enabled pygemc Python environment. The a/b families remain distinct;
original meshes retain the vacuumJacket6a component and three nanometre-sensitive plate contacts.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab as ml


EXCEPTIONS = ("shell2b", "shell3a", "shell5b", "shell6a")


def jacket_name(source_name):
    """Map archived engineering names to the active vacuum-jacket placement names."""
    return "vacuumJacket" if source_name == "shell1a" else source_name.replace("shell", "vacuumJacket", 1)


def load(path):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(path))
    return meshes


def hole_contours(vertices, faces):
    """Identify holes and the narrow slot on every axial cap, including buried steps."""
    contours = []
    for x in np.unique(vertices[:, 0]):
        cap = faces[np.all(abs(vertices[faces, 0] - x) < 1e-6, axis=1)]
        edges = {}
        for face in cap:
            for a, b in zip(face, np.roll(face, -1)):
                key = tuple(sorted((int(a), int(b))))
                edges[key] = edges.get(key, 0) + 1
        adjacent = {}
        for (a, b), count in edges.items():
            if count == 1:
                adjacent.setdefault(a, []).append(b)
                adjacent.setdefault(b, []).append(a)
        assert all(len(neighbors) == 2 for neighbors in adjacent.values())
        seen = set()
        for start in adjacent:
            if start in seen:
                continue
            loop, previous, current = [], None, start
            while current not in seen:
                seen.add(current)
                loop.append(current)
                following = next(i for i in adjacent[current] if i != previous)
                previous, current = current, following
            extent = np.ptp(vertices[loop, 1:], axis=0)
            if max(extent) < 200 or min(extent) < 2:
                contours.append(loop)
    return contours


def triangles(vertices, faces):
    """Coordinate keys independent of face winding and vertex numbering."""
    return {tuple(sorted(tuple(point) for point in triangle)) for triangle in vertices[faces]}


def simplify(source, target, genus):
    original = load(source)
    vertices = original.current_mesh().vertex_matrix()
    faces = original.current_mesh().face_matrix()
    contours = hole_contours(vertices, faces)
    protected = np.zeros(len(vertices), dtype=bool)
    for contour in contours:
        points = vertices[contour, 1:]
        low, high = points.min(0) - 0.5, points.max(0) + 0.5
        protected |= np.all((vertices[:, 1:] >= low) & (vertices[:, 1:] <= high), axis=1)
    for axis in (1, 2):
        protected |= (vertices[:, axis] == vertices[:, axis].min())
        protected |= (vertices[:, axis] == vertices[:, axis].max())
    meshes = ml.MeshSet()
    meshes.add_mesh(ml.Mesh(vertices, faces, v_scalar_array=protected.astype(float)))
    meshes.compute_selection_by_condition_per_vertex(condselect="q < 0.5")
    meshes.compute_selection_transfer_vertex_to_face(inclusive=True)
    selected = meshes.current_mesh().selected_face_number()
    meshes.meshing_decimation_quadric_edge_collapse(
        targetfacenum=selected - 4, preservetopology=True, preserveboundary=True,
        preservenormal=True, optimalplacement=False, planarquadric=True, qualitythr=0.3, selected=True)
    mesh = meshes.current_mesh()
    points, reduced = mesh.vertex_matrix(), mesh.face_matrix()
    assert triangles(vertices, faces[np.any(protected[faces], axis=1)]) <= triangles(points, reduced)
    assert all(np.any(np.all(points == point, axis=1)) for point in vertices[protected])
    assert np.array_equal(points.min(0), vertices.min(0))
    assert np.array_equal(points.max(0), vertices.max(0))
    topology = meshes.get_topological_measures()
    assert topology["boundary_edges"] == 0 and topology["is_mesh_two_manifold"]
    assert topology["genus"] == genus and topology["connected_components_number"] == 1
    meshes.compute_selection_by_self_intersections_per_face()
    assert meshes.current_mesh().selected_face_number() == 0
    meshes.save_current_mesh(str(target), binary=True)
    # Binary STL serialization must preserve every protected surface as well.
    stored_meshes = load(target)
    stored = stored_meshes.current_mesh()
    assert triangles(vertices, faces[np.any(protected[faces], axis=1)]) <= triangles(
        stored.vertex_matrix(), stored.face_matrix())
    return {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "output_sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
            "original_facets": len(faces), "optimized_facets": len(reduced),
            "protected_contours": len(contours), "protected_vertices": int(protected.sum()),
            "protected_faces": int(np.any(protected[faces], axis=1).sum()),
            "all_protected_triangles_unchanged": True, "bounds_unchanged": True,
            "original_volume_mm3": original.get_geometric_measures()["mesh_volume"],
            "optimized_volume_mm3": meshes.get_geometric_measures()["mesh_volume"],
            "topology": topology, "self_intersecting_faces": 0}


def write_catalogs(source, output):
    output.mkdir(parents=True, exist_ok=True)
    for path in sorted(source.glob("cad_*.gxml")):
        root = ET.parse(path).getroot()
        for row in root:
            name = row.get("name")
            if name == "vacuumJacket":
                name = "shell1a"
            elif name.startswith("vacuumJacket"):
                name = "shell" + name[len("vacuumJacket"):]
            if not (name.startswith("shell") and len(name) == 7):
                continue
            row.set("name", jacket_name(name))
            if name == "shell6a":
                continue
            row.set("position", "0.000*mm 0.000*mm 1273.270*mm")
            if name in EXCEPTIONS:
                row.attrib.pop("copyOf", None)
                row.set("rotation", "0*deg 180*deg 0*deg")
                continue
            sector = int(name[5])
            if sector > 1:
                row.set("copyOf", "vacuumJacket" if name.endswith("a") else "vacuumJacket1b")
                angle = 60 * (sector - 1)
                if angle > 180:
                    angle -= 360
                row.set("rotation", f"0*deg 180*deg {angle}*deg")
        lines = ["<gxml>"]
        for row in root:
            attrs = list(row.attrib.items())
            lines.append(f'  <volume {attrs[0][0]}="{attrs[0][1]}"')
            lines.extend(f'          {k}="{v}"' for k, v in attrs[1:-1])
            key, value = attrs[-1]
            lines.append(f'          {key}="{value}"/>')
        lines.append("</gxml>")
        (output / path.name).write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--catalogs", type=Path,
                        help="Optional input GXML directory for placement reproduction")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report = {}
    for name, output, genus in (("shell1a", "vacuumJacket", 38), ("shell1b", "vacuumJacket1b", 35)):
        report[output] = simplify(args.source / f"{name}.stl", args.output / f"{output}.stl", genus)
    for name in EXCEPTIONS:
        output = jacket_name(name)
        shutil.copy2(args.source / f"{name}.stl", args.output / f"{output}.stl")
        reason = "Preserve its additional disconnected component" if name == "shell6a" else (
            "Preserve original coordinates at a nanometre-sensitive plate contact")
        report[output] = {"unchanged": True, "reason": reason}
    (args.output / "vacuum_jacket_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    if args.catalogs:
        write_catalogs(args.catalogs, args.output / "catalog")


if __name__ == "__main__":
    main()
