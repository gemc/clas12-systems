#!/usr/bin/env python3
"""Share the five matching hub shields, retaining both distinct end pieces and every hole."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab as ml


NAMES = {1: "hub_shield1", 2: "hub_shield", **{i: f"hub_shield{i}" for i in range(3, 8)}}


def load(path):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(path))
    topology = meshes.get_topological_measures()
    assert topology["boundary_edges"] == 0 and topology["is_mesh_two_manifold"], path
    assert topology["genus"] == 1 and topology["connected_components_number"] == 1, path
    meshes.compute_selection_by_self_intersections_per_face()
    assert meshes.current_mesh().selected_face_number() == 0, path
    return meshes


def build(source, output, catalogs):
    original = {i: load(source / f"Shield{i}.stl") for i in range(1, 8)}
    canonical = original[2].current_mesh()
    reference = canonical.vertex_matrix()
    reference_faces = {tuple(sorted(face)) for face in canonical.face_matrix()}
    # Large absolute STL coordinates round the nominal 304.8 mm pitch upward. Recenter
    # the shared source, retaining its leading faces and rounding the far faces inward.
    # This removes artificial nanometre overlaps without changing any radial contour.
    shared_vertices = reference.copy()
    levels = np.unique(reference[:, 2])
    assert len(levels) == 4
    local = (levels + 1794.392).astype(np.float32)
    for j in (2, 3):
        if float(local[j]) > levels[j] + 1794.392:
            local[j] = np.nextafter(local[j], np.float32(-np.inf))
    local[0] = np.float32(float(local[2]) - 304.8)
    local[1] = np.float32(float(local[3]) - 304.8)
    assert all(float(local[j + 2]) - float(local[j]) <= 304.8 for j in (0, 1))
    for old, new in zip(levels, local):
        shared_vertices[reference[:, 2] == old, 2] = new
    records = []
    for index, meshes in original.items():
        path = source / f"Shield{index}.stl"
        vertices = meshes.current_mesh().vertex_matrix()
        faces = meshes.current_mesh().face_matrix()
        record = {"source": path.name, "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                  "name": NAMES[index], "facets": len(faces), "topology": meshes.get_topological_measures(),
                  "volume_mm3": meshes.get_geometric_measures()["mesh_volume"]}
        if 2 <= index <= 6:
            aligned = vertices + np.array([0, 0, 304.8 * (index - 2)])
            distances = np.linalg.norm(aligned[:, None] - reference[None, :], axis=2)
            indices = distances.argmin(1)
            assert len(set(indices)) == len(reference) == len(vertices), path
            error = float(distances[np.arange(len(vertices)), indices].max())
            assert error < 0.00025, (path, error)
            assert {tuple(sorted(face)) for face in indices[faces]} == reference_faces, path
            placed = shared_vertices[indices].copy()
            placed[:, 2] -= 1794.392 + 304.8 * (index - 2)
            final_error = float(np.linalg.norm(placed - vertices, axis=1).max())
            assert final_error < 0.00025
            record.update(max_vertex_error_mm=error, identical_mapped_connectivity=True,
                          final_vertex_error_mm=final_error, reference="hub_shield",
                          nominal_world_offset_mm=304.8 * (index - 2))
        else:
            assert len(faces) == 478
            record.update(distinct_end_profile=True)
        records.append(record)
    for index in (1, 7):
        shutil.copy2(source / f"Shield{index}.stl", output / f"{NAMES[index]}.stl")
    shared = ml.MeshSet()
    shared.add_mesh(ml.Mesh(shared_vertices, canonical.face_matrix()))
    shared.save_current_mesh(str(output / "hub_shield.stl"), binary=True)
    stored = load(output / "hub_shield.stl")
    saved = stored.current_mesh()
    assert np.array_equal(saved.vertex_matrix()[:, :2], reference[:, :2])
    assert np.array_equal(saved.face_matrix(), canonical.face_matrix())
    before = sum(row["volume_mm3"] for row in records)
    shared_volume = stored.get_geometric_measures()["mesh_volume"]
    after = records[0]["volume_mm3"] + 5 * shared_volume + records[6]["volume_mm3"]
    report = {"end_mesh_bytes_unchanged": True, "all_holes_retained": True,
              "radial_contours_and_connectivity_unchanged": True,
              "axial_recenter_mm": 1794.392, "world_source_position_mm": 3067.662,
              "source_axial_change_mm": (local.astype(float) - (levels + 1794.392)).tolist(),
              "shared_volume_mm3": shared_volume,
              "unique_facets_before": 4146, "unique_facets_after": 1594,
              "placed_facets_before": 4146, "placed_facets_after": 4146,
              "volume_before_mm3": before, "volume_after_mm3": after,
              "volume_change_percent": 100 * (after / before - 1), "shields": records}
    (output / "hub_shield_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    if catalogs:
        destination = output / "catalog"
        destination.mkdir(exist_ok=True)
        inverse = {name: i for i, name in NAMES.items()}
        for path in sorted(catalogs.glob("cad_*.gxml")):
            root = ET.parse(path).getroot()
            for row in root:
                name = row.get("name")
                index = int(name[-1]) if name in {f"Shield{i}" for i in NAMES} else inverse.get(name)
                if index is None:
                    continue
                row.set("name", NAMES[index])
                offset = 304.8 * (index - 2) if 2 <= index <= 6 else 0
                origin = 3067.662 if 2 <= index <= 6 else 1273.27
                row.set("position", f"0.000*mm 0.000*mm {origin + offset:.3f}*mm")
                row.set("rotation", "0*deg 180*deg 0*deg")
                row.attrib.pop("copyOf", None)
                if 3 <= index <= 6:
                    row.set("copyOf", "hub_shield")
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
