#!/usr/bin/env python3
"""Fill magnet fastener holes and retriangulate the separate plates and vacuum jackets.

Run with a mesh-enabled pygemc Python environment. The two original volumes retain their engineering
rims, main apertures, placements, and axial separation.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pymeshlab as ml


SOURCE_HASHES = {
    "DownstreamShieldingPlate": "74bdd1d9524c2201121a77affb2df26d7c8901a97f12bb89f0aa824835aae29a",
    "DownstreamVacuumJacket": "d369db3e8f3a5bf79897e890d8106440db0138e7f1bb61bd449846a4cfcbd849",
    "UpstreamShieldingPlate": "45b5303255fbfdd4b1f6df5c2d086930cb5e12c1466cb581c328df004824ae9c",
    "UpstreamVacuumJacket": "af1bdbe5b7de5104c8d9fbc64f255f771bb0dac8d290e94aeaa07a33d7d4544e",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inventory(path):
    ms = ml.MeshSet()
    ms.load_new_mesh(str(path))
    mesh = ms.current_mesh()
    vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
    triangles = vertices[faces]
    area = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                   triangles[:, 2] - triangles[:, 0]), axis=1)
    ms.compute_selection_by_self_intersections_per_face()
    return {"sha256": sha256(path), "triangles": mesh.face_number(), "bytes": path.stat().st_size,
            "bounds_mm": [vertices.min(0).tolist(), vertices.max(0).tolist()],
            "volume_mm3": ms.get_geometric_measures()["mesh_volume"],
            "topology": ms.get_topological_measures(), "zero_area_triangles": int((area == 0).sum()),
            "self_intersecting_faces": mesh.selected_face_number()}


def rim_angles(points):
    angles = np.mod(np.arctan2(points[:, 1], points[:, 0]), 2 * np.pi)
    angles[(angles < 1e-12) | (angles > 2 * np.pi - 1e-12)] = 0
    return angles


def ring(vertices, z, radius, count):
    radial = np.linalg.norm(vertices[:, :2], axis=1)
    selected = vertices[(abs(vertices[:, 2] - z) < 0.001) & (abs(radial - radius) < 0.001)]
    selected = selected[np.argsort(rim_angles(selected))]
    if len(selected) != count:
        raise ValueError(f"Unexpected rim at z={z}, r={radius}: {len(selected)} vertices")
    return selected


def strip(first, second, start_first, start_second):
    """Triangulate between nested circular/convex rims without moving their vertices."""
    angles = [rim_angles(r) for r in (first, second)]
    sizes = len(first), len(second)
    i = j = 0
    faces = []
    while i < sizes[0] or j < sizes[1]:
        next_i = angles[0][i + 1] if i + 1 < sizes[0] else angles[0][0] + 2 * np.pi
        next_j = angles[1][j + 1] if j + 1 < sizes[1] else angles[1][0] + 2 * np.pi
        a, b = start_first + i % sizes[0], start_second + j % sizes[1]
        if i < sizes[0] and (j == sizes[1] or next_i < next_j):
            faces.append([a, start_first + (i + 1) % sizes[0], b])
            i += 1
        else:
            faces.append([a, start_second + (j + 1) % sizes[1], b])
            j += 1
    return faces


def closed_profile(rings):
    """Connect consecutive profile rims, then close the final rim back to the first."""
    offsets = np.cumsum([0] + [len(r) for r in rings]).tolist()
    points = np.vstack(rings)
    faces = []
    for i in range(len(rings)):
        j = (i + 1) % len(rings)
        faces.extend(strip(rings[i], rings[j], offsets[i], offsets[j]))
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(points, np.array(faces)))
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()["mesh_volume"] < 0:
        ms.meshing_invert_face_orientation()
    return ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix()


def polygon_area(rim):
    x, y = rim[:, 0], rim[:, 1]
    return abs(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))) / 2


def upstream_jacket(vertices, faces):
    """Fill six blind drilled pockets while retaining every other non-cap triangle exactly."""
    import vtk
    from vtk.util.numpy_support import numpy_to_vtk, vtk_to_numpy

    upper = vertices[:, 2].max()
    radius = np.linalg.norm(vertices[:, :2], axis=1)
    drilled = (radius > 90) & (radius < 125)
    cap = np.all(abs(vertices[faces, 2] - upper) < 0.001, axis=1)
    keep = ~cap & ~np.any(drilled[faces], axis=1)
    edges = np.sort(np.concatenate([faces[keep][:, [0, 1]], faces[keep][:, [1, 2]],
                                    faces[keep][:, [2, 0]]]), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    neighbors = {}
    for a, b in unique[counts == 1]:
        neighbors.setdefault(a, []).append(b)
        neighbors.setdefault(b, []).append(a)
    if len(neighbors) != 110 or any(len(adjacent) != 2 for adjacent in neighbors.values()):
        raise ValueError("Expected only the two original cap boundary loops")
    unseen = set(neighbors)
    loops = []
    while unseen:
        loop = [min(unseen)]
        previous = None
        current = loop[0]
        while True:
            following = next(i for i in neighbors[current] if i != previous)
            if following == loop[0]:
                break
            loop.append(following)
            previous, current = current, following
        unseen -= set(loop)
        loops.append(loop)
    loops.sort(key=lambda ids: polygon_area(vertices[ids]), reverse=True)
    if list(map(len, loops)) != [60, 50]:
        raise ValueError("Unexpected upstream cap contours")
    lines = vtk.vtkCellArray()
    for index, loop in enumerate(loops):
        xy = vertices[loop, :2]
        signed_area = np.sum(xy[:, 0] * np.roll(xy[:, 1], -1) - xy[:, 1] * np.roll(xy[:, 0], -1))
        if (signed_area > 0) != (index == 0):
            loop = loop[::-1]
        for a, b in zip(loop, loop[1:] + loop[:1]):
            lines.InsertNextCell(2)
            lines.InsertCellPoint(int(a))
            lines.InsertCellPoint(int(b))
    points = vtk.vtkPoints()
    points.SetData(numpy_to_vtk(vertices, deep=True))
    contours = vtk.vtkPolyData()
    contours.SetPoints(points)
    contours.SetLines(lines)
    triangles = vtk.vtkCellArray()
    if not vtk.vtkContourTriangulator.TriangulateContours(contours, 0, 110, triangles, (0, 0, 1)):
        raise ValueError("Could not triangulate the original reentrant outer contour")
    cap_faces = vtk_to_numpy(triangles.GetConnectivityArray()).reshape(-1, 3)
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertices, np.vstack([faces[keep], cap_faces])))
    ms.meshing_remove_unreferenced_vertices()
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()["mesh_volume"] < 0:
        ms.meshing_invert_face_orientation()
    return (ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix(), int(keep.sum()))


def build(source, output, pair="downstream"):
    output.mkdir(parents=True, exist_ok=True)
    parts = []
    report = {}
    prefix = "Downstream" if pair == "downstream" else "Upstream"
    names = (prefix + "ShieldingPlate", prefix + "VacuumJacket")
    for name in names:
        original = source / f"{name}.stl"
        before = inventory(original)
        if before["sha256"] != SOURCE_HASHES[name]:
            raise ValueError(f"Unexpected engineering input: {original}")
        ms = ml.MeshSet()
        ms.load_new_mesh(str(original))
        vertices = ms.current_mesh().vertex_matrix()
        lower, upper = vertices[:, 2].min(), vertices[:, 2].max()
        expected = None
        preserved_faces = None
        if name.endswith("ShieldingPlate"):
            inner = [ring(vertices, z, 76.35, 51) for z in (lower, upper)]
            outer = [ring(vertices, z, 175, 76) for z in (lower, upper)]
            rims = [inner[0], outer[0], outer[1], inner[1]]
            expected = (polygon_area(outer[0]) - polygon_area(inner[0])) * (upper - lower)
            holes = {"through_holes_filled": 8, "blind_holes_filled": 0}
        elif pair == "downstream":
            shoulder = -3623.068115234375
            inner = [ring(vertices, z, 63.5, 46) for z in (lower, upper)]
            outer = [ring(vertices, z, 230, 87) for z in (lower, shoulder)]
            hexagon = [ring(vertices, z, 201.443, 6) for z in (shoulder, upper)]
            rims = [inner[0], outer[0], outer[1], hexagon[0], hexagon[1], inner[1]]
            if not np.array_equal(hexagon[0][:, :2], hexagon[1][:, :2]):
                raise ValueError("Jacket hexagonal step changes cross-section")
            expected = ((polygon_area(outer[0]) - polygon_area(inner[0])) * (shoulder - lower)
                        + (polygon_area(hexagon[0]) - polygon_area(inner[0])) * (upper - shoulder))
            holes = {"through_holes_filled": 0, "blind_holes_filled": 6}
        else:
            points, faces, preserved_faces = upstream_jacket(vertices, ms.current_mesh().face_matrix())
            holes = {"through_holes_filled": 0, "blind_holes_filled": 6}
        if expected is not None:
            for edges in (inner, outer):
                if not np.allclose(edges[0][:, :2], edges[1][:, :2], rtol=0, atol=1e-9):
                    raise ValueError("Engineering rim changes cross-section")
            points, faces = closed_profile(rims)
        part = output / f"{name}.stl"
        mesh = ml.MeshSet()
        mesh.add_mesh(ml.Mesh(points, faces))
        mesh.save_current_mesh(str(part))
        after = inventory(part)
        if (after["bounds_mm"] != before["bounds_mm"] or after["topology"]["genus"] != 1
                or after["topology"]["boundary_edges"] or not after["topology"]["is_mesh_two_manifold"]
                or after["self_intersecting_faces"] or after["zero_area_triangles"]
                or (expected is not None and not np.isclose(after["volume_mm3"], expected, rtol=1e-9))):
            raise ValueError(f"Failed filled-part checks: {name}")
        report[name] = {"original": before, "filled": after, "analytic_volume_mm3": expected,
                        "preserved_non_cap_faces": preserved_faces, **holes}
        parts.append((points, faces))
    gap = max(parts[0][0][:, 2].min(), parts[1][0][:, 2].min()) - min(
        parts[0][0][:, 2].max(), parts[1][0][:, 2].max())
    if gap <= 0:
        raise ValueError("The engineering axial gap must remain open")
    report["retained_gap_mm"] = gap
    report["source_faces"] = sum(report[name]["original"]["triangles"] for name in names)
    report["optimized_faces"] = sum(report[name]["filled"]["triangles"] for name in names)
    (output / f"{pair}_plate_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"Plate and jacket: {report['source_faces']} -> {report['optimized_faces']} triangles; "
          f"gap {gap:.8f} mm; separate original names")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True, help="Archived engineering mesh directory")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pair", choices=("downstream", "upstream"), default="downstream")
    args = parser.parse_args()
    build(args.source, args.output, args.pair)


if __name__ == "__main__":
    main()
