#!/usr/bin/env python3
"""Share the two hub-cover meshes without altering any surface or hole."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab as ml

from build_coils import boundary


REFERENCES = {1: 1, 2: 1, 3: 3, 4: 1, 5: 1, 6: 3}


def mesh(path, genus):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(path))
    topology = meshes.get_topological_measures()
    assert topology["boundary_edges"] == 0 and topology["is_mesh_two_manifold"], path
    assert topology["genus"] == genus and topology["connected_components_number"] == 1, path
    meshes.compute_selection_by_self_intersections_per_face()
    assert meshes.current_mesh().selected_face_number() == 0, path
    return meshes


def build(source, output, catalogs):
    references = {i: mesh(source / f"Plate{i}.stl", int(i == 3)) for i in (1, 3)}
    records = []
    for sector, reference_sector in REFERENCES.items():
        path = source / f"Plate{sector}.stl"
        current = mesh(path, int(reference_sector == 3))
        vertices = current.current_mesh().vertex_matrix()
        faces = current.current_mesh().face_matrix()
        reference = references[reference_sector].current_mesh().vertex_matrix()
        reference_faces = references[reference_sector].current_mesh().face_matrix()
        assert len(faces) == len(reference_faces) == (150 if reference_sector == 3 else 12)
        angle = np.radians(60 * (sector - reference_sector))
        rotation = np.array([[np.cos(angle), np.sin(angle), 0],
                             [-np.sin(angle), np.cos(angle), 0], [0, 0, 1]])
        distances = np.linalg.norm((vertices @ rotation)[:, None] - reference[None, :], axis=2)
        indices = distances.argmin(1)
        assert len(set(indices)) == len(reference) == len(vertices), path
        error = float(distances[np.arange(len(vertices)), indices].max())
        assert error < 0.00001, (path, error)
        canonical = {tuple(sorted(face)) for face in reference_faces}
        mapped = {tuple(sorted(face)) for face in indices[faces]}
        removed, added = canonical - mapped, mapped - canonical
        if removed or added:
            assert len(removed) == len(added) == 2 and boundary(removed) == boundary(added), path
            changed = sorted({i for face in removed | added for i in face})
            assert len(changed) == 4
            points = reference[changed]
            normal = np.cross(points[1] - points[0], points[2] - points[0])
            assert abs(np.dot(points[3] - points[0], normal)) / np.linalg.norm(normal) < 1e-9
        records.append({"source": path.name, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "reference": f"hubCover{reference_sector}", "max_vertex_error_mm": error,
                        "different_flat_triangles": len(removed), "facets": len(faces),
                        "topology": current.get_topological_measures(),
                        "volume_mm3": current.get_geometric_measures()["mesh_volume"]})
    for sector in (1, 3):
        shutil.copy2(source / f"Plate{sector}.stl", output / f"hubCover{sector}.stl")
    before = sum(row["volume_mm3"] for row in records)
    after = 4 * records[0]["volume_mm3"] + 2 * records[2]["volume_mm3"]
    report = {"canonical_bytes_unchanged": True, "all_hole_surfaces_unchanged": True,
              "unique_facets_before": 348, "unique_facets_after": 162,
              "placed_facets_before": 348, "placed_facets_after": 348,
              "volume_before_mm3": before, "volume_after_mm3": after,
              "volume_change_percent": 100 * (after / before - 1), "sectors": records}
    (output / "hub_cover_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    if catalogs:
        destination = output / "catalog"
        destination.mkdir(exist_ok=True)
        for path in sorted(catalogs.glob("cad_*.gxml")):
            root = ET.parse(path).getroot()
            for row in root:
                name = row.get("name").replace("hubCover", "Plate", 1)
                if name not in {f"Plate{i}" for i in REFERENCES}:
                    continue
                sector = int(name[-1])
                reference = REFERENCES[sector]
                row.set("name", f"hubCover{sector}")
                row.set("position", "0.000*mm 0.000*mm 1273.270*mm")
                angle = 60 * (sector - reference)
                if angle > 180:
                    angle -= 360
                row.set("rotation", f"0*deg 180*deg {angle}*deg")
                if sector != reference:
                    row.set("copyOf", f"hubCover{reference}")
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
