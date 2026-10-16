"""Restore the missing radial-port wall and simplify the inner Moller-cone extension."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pymeshlab as ml

NAME = "moller-cone-extension-inner"


def stitch_port(vertices, faces):
    """Bridge the two port rims without capping either the port or the beam passage."""
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    boundary = unique[counts == 1]
    adjacency = {}
    for a, b in boundary:
        adjacency.setdefault(int(a), set()).add(int(b))
        adjacency.setdefault(int(b), set()).add(int(a))
    if len(boundary) != 75 or any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError("Expected two simple radial-port rims")
    unseen, loops = set(adjacency), []
    while unseen:
        start = min(unseen)
        previous, current, loop = None, start, []
        while current not in loop:
            loop.append(current)
            choices = adjacency[current] - ({previous} if previous is not None else set())
            previous, current = current, min(choices)
        if current != start:
            raise ValueError("Unexpected boundary branching")
        unseen -= set(loop)
        loops.append(np.array(loop))
    if sorted(map(len, loops)) != [35, 40]:
        raise ValueError("Expected the original 35- and 40-vertex port rims")
    loops.sort(key=lambda ids: np.linalg.norm(vertices[ids, :2], axis=1).mean())
    port_vertices = np.concatenate(loops)
    z0 = float(vertices[port_vertices, 2].max() - 6.35)
    angles = []
    for index, ring in enumerate(loops):
        angle = np.mod(np.arctan2(vertices[ring, 2] - z0, vertices[ring, 1]), 2*np.pi)
        order = np.argsort(angle)
        loops[index] = ring[order]
        angles.append(angle[order])
    a, b = loops
    aa, bb = angles
    additions, i, j = [], 0, 0
    while i < len(a) or j < len(b):
        next_a = aa[i + 1] if i + 1 < len(a) else aa[0] + 2*np.pi
        next_b = bb[j + 1] if j + 1 < len(b) else bb[0] + 2*np.pi
        if i < len(a) and (j == len(b) or next_a < next_b):
            additions.append([a[i % len(a)], a[(i + 1) % len(a)], b[j % len(b)]])
            i += 1
        else:
            additions.append([a[i % len(a)], b[(j + 1) % len(b)], b[j % len(b)]])
            j += 1
    if len(additions) != 75:
        raise ValueError("Unexpected radial-port wall triangulation")
    return np.vstack([faces, additions]), port_vertices, z0


def build_extension_inner(source, output, reference_output=None):
    from build_cad_meshes import inventory, sharp_face_quality

    original = Path(source)/"inner-assembly.stl"
    before = inventory(original)
    if before["sha256"] != "7b81f79279cbc2703989379688e6eefac5439dfaa3bdd5275d13bbe0505099c2":
        raise ValueError("Unexpected inner-extension engineering mesh")
    ms = ml.MeshSet()
    ms.load_new_mesh(str(original))
    mesh = ms.current_mesh()
    vertices = mesh.vertex_matrix()
    faces, port_vertices, port_z = stitch_port(vertices, mesh.face_matrix())
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertices, faces))
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()["mesh_volume"] < 0:
        ms.meshing_invert_face_orientation()
    with TemporaryDirectory() as scratch:
        reference_path = Path(scratch)/"repaired-reference.stl"
        ms.save_current_mesh(str(reference_path))
        reference = inventory(reference_path)
        mesh = ms.current_mesh()
        vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
        fixed = (sharp_face_quality(mesh) == 0) | np.isin(faces, port_vertices).any(axis=1)
        protected = vertices[faces[fixed]]
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=(~fixed).astype(float)))
        ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=12500-int(fixed.sum()),
            preservenormal=True, preservetopology=True, preserveboundary=True, planarquadric=True,
            autoclean=True, selected=True)
        ms.meshing_re_orient_faces_coherently()
        result = Path(output)/(NAME+".stl")
        ms.save_current_mesh(str(result))
        after = inventory(result)
        saved = ml.MeshSet()
        saved.load_new_mesh(str(result))
        mesh = saved.current_mesh()
        triangles = mesh.vertex_matrix()[mesh.face_matrix()]
        saved_faces = {tuple(sorted(map(tuple, triangle))) for triangle in triangles}
        if not all(tuple(sorted(map(tuple, triangle))) in saved_faces for triangle in protected):
            raise ValueError("Changed a protected port or sharp-edge face")
        area2 = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0],
                                       triangles[:, 2]-triangles[:, 0]), axis=1)
        longest = np.max([np.linalg.norm(triangles[:, a]-triangles[:, b], axis=1)
                          for a, b in ((0, 1), (1, 2), (2, 0))], axis=0)
        minimum_altitude = float(np.min(area2/longest))
        comparison = ml.MeshSet()
        comparison.load_new_mesh(str(reference_path))
        comparison.load_new_mesh(str(result))
        distances = [comparison.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
            samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
        if reference_output is not None:
            reference_output.parent.mkdir(parents=True, exist_ok=True)
            reference_output.write_bytes(reference_path.read_bytes())
    change = 100*(after["volume_mm3"]/reference["volume_mm3"]-1)
    for label, row in (("reference", reference), ("optimized", after)):
        topology = row["topology"]
        if (topology["boundary_edges"] or topology["genus"] != 3 or not topology["is_mesh_two_manifold"]
                or topology["connected_components_number"] != 1 or row["zero_area_triangles"]
                or row["self_intersecting_faces"] or row["bounds_mm"] != before["bounds_mm"]):
            raise ValueError(f"Inner-extension {label} failed topology, shape, or bounds checks")
    if abs(change) > .01 or max(d["max"] for d in distances) > .05 or minimum_altitude < 1e-8:
        raise ValueError("Inner-extension decimation failed shape, material, or facet checks")
    report = {NAME: {"original_name": "inner-assembly", "before": before, "after": after,
        "repaired_reference": reference, "sampled_distances_mm": distances,
        "decimation_volume_change_percent": change, "protected_faces": int(fixed.sum()),
        "minimum_triangle_altitude_mm": minimum_altitude,
        "repair": {"added_port_wall_triangles": 75, "rim_vertices": [35, 40],
            "port_axis": "x", "port_center_z_mm": port_z, "nominal_port_radius_mm": 6.35,
            "original_vertices_retained": True, "beam_passage_and_ports_capped": False},
        "volume_caveat": "The open original has no valid solid volume; changes use the repaired reference."}}
    (Path(output)/"extension_inner_mesh_health.json").write_text(json.dumps(report, indent=2)+"\n")
    print(f"{NAME}: {before['triangles']} -> {after['triangles']} triangles; "
          f"volume vs repaired reference {change:.6g}%", flush=True)
