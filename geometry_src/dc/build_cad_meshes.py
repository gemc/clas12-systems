#!/usr/bin/env python3
"""Verify DC region-1 meshes and fit one STL per group with five passive copies.

Use the mesh-enabled pygemc Python environment. Originals are archived in clas12Tags;
The optimization shares solids while retaining engineering surfaces and their openings.
"""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab


def mesh(path):
    meshes = pymeshlab.MeshSet()
    meshes.load_new_mesh(str(path))
    current = meshes.current_mesh()
    vertices, faces = current.vertex_matrix(), current.face_matrix()
    support = path.stem.endswith("support")
    assert vertices.shape == ((499, 3) if support else (12, 3)), path
    assert faces.shape == ((1006, 3) if support else (20, 3)), path
    topology = meshes.get_topological_measures()
    assert topology["boundary_edges"] == 0 and topology["is_mesh_two_manifold"], path
    assert topology["connected_components_number"] == (2 if support else 1), path
    assert topology["genus"] == (4 if support else 0), path
    return vertices, faces


def build_group(source_dir, output, group, round_angles):
    canonical = 1 if group == "support" else 5
    source = source_dir / f"dcs{canonical}r1{group}.stl"
    reference, faces = mesh(source)
    volumes = []
    root = ET.Element("gxml")
    report = {"canonical": source.name, "stored_facets_before": 6 * len(faces),
              "stored_facets_after": len(faces),
              "placed_facets_before": 6 * len(faces), "placed_facets_after": 6 * len(faces),
              "integer_angles": round_angles, "position_decimal_places": 3, "sectors": []}
    flip = np.diag([-1., 1., -1.])
    for sector in range(1, 7):
        name = f"dcs{sector}r1{group}"
        original = source_dir / f"{name}.stl"
        target, target_faces = mesh(original)
        if group == "support":
            phi = np.radians(-60 * (sector - 1))
            rotation = np.array([[np.cos(phi), np.sin(phi), 0],
                                 [-np.sin(phi), np.cos(phi), 0], [0, 0, 1]])
            translation = target.mean(0) - reference.mean(0) @ rotation
            for _ in range(30):
                transformed = reference @ rotation + translation
                distances = np.linalg.norm(transformed[:, None] - target[None, :], axis=2)
                indices = distances.argmin(1)
                matched = target[indices]
                a, b = reference - reference.mean(0), matched - matched.mean(0)
                u, _, vt = np.linalg.svd(a.T @ b)
                rotation = u @ np.diag([1., 1., np.linalg.det(u @ vt)]) @ vt
                translation = matched.mean(0) - reference.mean(0) @ rotation
            assert len(set(indices)) == len(target), name
        else:
            # Exported back-membrane corner order is consistent between sectors.
            matched = target
            a, b = reference - reference.mean(0), target - target.mean(0)
            u, _, vt = np.linalg.svd(a.T @ b)
            rotation = u @ np.diag([1., 1., np.linalg.det(u @ vt)]) @ vt
            translation = target.mean(0) - reference.mean(0) @ rotation
        fitted = reference @ rotation + translation
        errors = np.linalg.norm(fitted - matched, axis=1)
        assert errors.max() < 0.00013, (name, errors.max())
        # Row-vector local-to-world transform: old placement was Ry(180), then +1273.27 mm z.
        frame = rotation @ flip
        position = translation @ flip + [0., 0., 1273.27]
        position = np.round(position, 3)
        position[position == 0] = 0
        # G4's passive matrix is Rz(z) Ry(y) Rx(x); the physical transform is its inverse.
        x = np.arctan2(frame[2, 1], frame[2, 2])
        y = np.arctan2(-frame[2, 0], np.hypot(frame[0, 0], frame[1, 0]))
        z = np.arctan2(frame[1, 0], frame[0, 0])
        cx, cy, cz = np.cos([x, y, z])
        sx, sy, sz = np.sin([x, y, z])
        rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
        rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
        assert np.max(abs(rz @ ry @ rx - frame)) < 1e-12
        angles = np.round(np.degrees([x, y, z]), 6)
        if round_angles:
            angles = np.round(angles)
        angles[angles == -180] = 180
        angles[angles == 0] = 0
        cx, cy, cz = np.cos(np.radians(angles))
        sx, sy, sz = np.sin(np.radians(angles))
        rounded_frame = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]) @ np.array(
            [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]) @ np.array(
            [[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
        world = reference @ rounded_frame + position
        world_errors = np.linalg.norm(world - (matched @ flip + [0., 0., 1273.27]), axis=1)
        assert world_errors.max() < (4 if round_angles else 0.001)
        material = "G4_Al" if group == "support" else "G4_KAPTON"
        attrs = {"name": name, "color": "ffaaff", "material": material,
                 "position": " ".join(f"{v:.3f}*mm" for v in position),
                 "rotation": " ".join(f"{v:g}*deg" if v == int(v) else f"{v:.6f}*deg" for v in angles)}
        if sector != canonical:
            attrs["copyOf"] = source.stem
        else:
            attrs["rotation"] = "0*deg 180*deg 0*deg"
        ET.SubElement(root, "volume", attrs)
        triangles = target[target_faces]
        volume = float(np.einsum("ij,ij->i", triangles[:, 0],
                                 np.cross(triangles[:, 1], triangles[:, 2])).sum() / 6)
        volumes.append(volume)
        report["sectors"].append({"name": name, "sha256": hashlib.sha256(original.read_bytes()).hexdigest(),
                                  "max_vertex_error_mm": float(errors.max()), "volume_mm3": volume,
                                  "max_rounded_world_error_mm": float(world_errors.max()),
                                  "position": position.tolist(), "passive_rotation": frame.tolist()})
    report["volume_before_mm3"] = sum(volumes)
    report["volume_after_mm3"] = 6 * volumes[canonical - 1]
    report["volume_change_percent"] = 100 * (report["volume_after_mm3"] / sum(volumes) - 1)
    shutil.copy2(source, output / source.name)
    (output / f"{group}_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    return root


def write_placements(root, path):
    # Keep attributes wrapped for review; XML whitespace does not affect the placement strings.
    lines = ["<gxml>"]
    for row in root:
        attrs = list(row.attrib.items())
        lines.extend(["  <volume " + " ".join(f'{k}="{v}"' for k, v in attrs[:3]),
                      *[f'    {k}="{v}"' for k, v in attrs[3:]], "  />"])
    lines.append("</gxml>")
    path.write_text("\n".join(lines) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--group", choices=("back", "support", "all"), default="back")
    parser.add_argument("--round-angles", action="store_true",
                        help="Use integer angles after validating overlaps in the surrounding assembly")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    root = ET.Element("gxml")
    for group in (("back", "support") if args.group == "all" else (args.group,)):
        root.extend(build_group(args.source, args.output, group, args.round_angles))
    write_placements(root, args.output / "cad_default.gxml")


if __name__ == "__main__":
    main()
