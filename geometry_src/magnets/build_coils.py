#!/usr/bin/env python3
"""Verify six torus coils and share one unchanged STL while retaining every opening."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab as ml


def load(path):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(path))
    topology = meshes.get_topological_measures()
    assert topology["boundary_edges"] == 0 and topology["is_mesh_two_manifold"], path
    assert topology["genus"] == 1 and topology["connected_components_number"] == 1, path
    meshes.compute_selection_by_self_intersections_per_face()
    assert meshes.current_mesh().selected_face_number() == 0, path
    return meshes


def boundary(faces):
    edges = {}
    for face in faces:
        for a, b in zip(face, np.roll(face, -1)):
            key = tuple(sorted((a, b)))
            edges[key] = edges.get(key, 0) + 1
    return {edge for edge, count in edges.items() if count == 1}


def build(source, output, catalogs):
    canonical = load(source / "coil1.stl")
    reference = canonical.current_mesh().vertex_matrix()
    faces = canonical.current_mesh().face_matrix()
    reference_faces = {tuple(sorted(face)) for face in faces}
    assert reference.shape == (508, 3) and faces.shape == (1016, 3)
    records = []
    for sector in range(1, 7):
        path = source / f"coil{sector}.stl"
        meshes = load(path)
        vertices = meshes.current_mesh().vertex_matrix()
        source_faces = meshes.current_mesh().face_matrix()
        angle = np.radians(60 * (sector - 1))
        rotation = np.array([[np.cos(angle), np.sin(angle), 0],
                             [-np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        aligned = vertices @ rotation
        distances = np.linalg.norm(aligned[:, None] - reference[None, :], axis=2)
        indices = distances.argmin(1)
        assert len(vertices) == len(reference) and len(set(indices)) == len(reference), path
        error = float(distances[np.arange(len(vertices)), indices].max())
        assert error < 0.00025, (path, error)
        mapped = {tuple(sorted(face)) for face in indices[source_faces]}
        removed, added = reference_faces - mapped, mapped - reference_faces
        if removed or added:
            # Two exports choose the other diagonal of one flat side quadrilateral.
            assert len(removed) == len(added) == 2, path
            assert boundary(removed) == boundary(added), path
            vertices_changed = sorted({i for face in removed | added for i in face})
            assert len(vertices_changed) == 4, path
            points = reference[vertices_changed]
            normal = np.cross(points[1] - points[0], points[2] - points[0])
            plane_error = abs(np.dot(points[3] - points[0], normal)) / np.linalg.norm(normal)
            assert plane_error < 1e-9, (path, plane_error)
        records.append({"source": path.name, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "max_vertex_error_mm": error, "different_flat_triangles": len(removed),
                        "facets": len(source_faces), "topology": meshes.get_topological_measures(),
                        "volume_mm3": meshes.get_geometric_measures()["mesh_volume"]})
    shutil.copy2(source / "coil1.stl", output / "coil.stl")
    original_volume = sum(row["volume_mm3"] for row in records)
    shared_volume = 6 * records[0]["volume_mm3"]
    report = {"source": "coil1.stl", "output": "coil.stl", "canonical_bytes_unchanged": True,
              "all_openings_retained": True, "unique_facets_before": 6096, "unique_facets_after": 1016,
              "placed_facets_before": 6096, "placed_facets_after": 6096,
              "volume_before_mm3": original_volume, "volume_after_mm3": shared_volume,
              "volume_change_percent": 100 * (shared_volume / original_volume - 1), "sectors": records}
    (output / "coil_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    if catalogs:
        destination = output / "catalog"
        destination.mkdir(exist_ok=True)
        for path in sorted(catalogs.glob("cad_*.gxml")):
            root = ET.parse(path).getroot()
            for row in root:
                name = row.get("name")
                if name == "coil":
                    name = "coil1"
                if name not in {f"coil{i}" for i in range(1, 7)}:
                    continue
                sector = int(name[-1])
                row.set("name", "coil" if sector == 1 else name)
                row.set("position", "0.000*mm 0.000*mm 1273.270*mm")
                angle = 60 * (sector - 1)
                if angle > 180:
                    angle -= 360
                row.set("rotation", f"0*deg 180*deg {angle}*deg")
                if sector > 1:
                    row.set("copyOf", "coil")
            lines = ["<gxml>"]
            for row in root:
                attrs = list(row.attrib.items())
                lines.append(f'  <volume {attrs[0][0]}="{attrs[0][1]}"')
                lines.extend(f'          {k}="{v}"' for k, v in attrs[1:-1])
                key, value = attrs[-1]
                lines.append(f'          {key}="{value}"/>')
            lines.append("</gxml>")
            (destination / path.name).write_text("\n".join(lines) + "\n")


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
