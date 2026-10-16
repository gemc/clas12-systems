"""Restore the tungsten add-on port wall and simplify away from its engineering interfaces."""

import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pymeshlab as ml

NAME = "moller-cone-extension-tungsten-addon"
ORIGINAL_SHA = "3e4378742de0f334b77d1f2bef8f2876f025118ea615706ceffa94dc1a980815"
MATING_SHA = "6640a8179f48d30242da0fafcc7c4f4c1be97022a73c4d94e0291221dcae96e0"


def stitch_port(vertices, faces):
    """Bridge the 33- and 35-vertex rims of the inclined radial port, retaining every vertex."""
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    boundary = unique[counts == 1]
    adjacency = {}
    for a, b in boundary:
        adjacency.setdefault(int(a), set()).add(int(b))
        adjacency.setdefault(int(b), set()).add(int(a))
    if len(boundary) != 68 or any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError("Expected two simple tungsten-port rims")
    unseen, loops = set(adjacency), []
    while unseen:
        start = min(unseen)
        previous, current, loop = None, start, []
        while current not in loop:
            loop.append(current)
            choices = adjacency[current] - ({previous} if previous is not None else set())
            previous, current = current, min(choices)
        if current != start:
            raise ValueError("Unexpected port boundary branching")
        unseen -= set(loop)
        loops.append(np.array(loop))
    if sorted(map(len, loops)) != [33, 35]:
        raise ValueError("Expected the original 33- and 35-vertex rims")
    loops.sort(key=lambda ids: np.linalg.norm(vertices[ids, :2], axis=1).mean())
    slope = np.tan(np.deg2rad(4.5))
    intercept = -124.150890
    angles = []
    for index, ring in enumerate(loops):
        transverse = (vertices[ring, 2] - slope*vertices[ring, 1] - intercept)/np.sqrt(1+slope*slope)
        angle = np.mod(np.arctan2(transverse, vertices[ring, 0]), 2*np.pi)
        order = np.argsort(angle)
        loops[index] = ring[order]
        angles.append(angle[order])
    a, b = loops
    aa, bb = angles
    additions, i, j = [], 0, 0
    while i < len(a) or j < len(b):
        next_a = aa[i+1] if i+1 < len(a) else aa[0]+2*np.pi
        next_b = bb[j+1] if j+1 < len(b) else bb[0]+2*np.pi
        if i < len(a) and (j == len(b) or next_a < next_b):
            additions.append([a[i % len(a)], a[(i+1) % len(a)], b[j % len(b)]])
            i += 1
        else:
            additions.append([a[i % len(a)], b[(j+1) % len(b)], b[j % len(b)]])
            j += 1
    return np.vstack([faces, additions]), np.concatenate(loops)


def build_extension_tungsten(source, output, reference_output=None):
    from build_cad_meshes import inventory, sharp_face_quality

    original = Path(source)/"outer-cone.stl"
    before = inventory(original)
    if before["sha256"] != ORIGINAL_SHA:
        raise ValueError("Unexpected tungsten add-on engineering mesh")
    neighbor = Path(__file__).parent/"stls/moller_cone.stl"
    archived_neighbor = Path(source)/"ft_joint_inputs_20261016/moller_cone.stl"
    if archived_neighbor.exists():
        # Reproduce the measured pre-clearance optimization; apply ft_joints as the final build pass.
        neighbor = archived_neighbor
    if hashlib.sha256(neighbor.read_bytes()).hexdigest() != MATING_SHA:
        raise ValueError("Reassess mating-face protection against the changed main Moller cone")
    ms = ml.MeshSet()
    ms.load_new_mesh(str(original))
    mesh = ms.current_mesh()
    vertices = mesh.vertex_matrix()
    faces, port_vertices = stitch_port(vertices, mesh.face_matrix())
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
        fixed |= (vertices[faces, 2] < -169.5).any(axis=1)
        ms.load_new_mesh(str(neighbor))
        ms.compute_scalar_by_distance_from_another_mesh_per_vertex(measuremesh=0, refmesh=1, signeddist=False)
        ms.set_current_mesh(0)
        mating = (ms.current_mesh().vertex_scalar_array()[faces] < .25).any(axis=1)
        fixed |= mating
        protected = vertices[faces[fixed]]
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=(~fixed).astype(float)))
        ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=12000-int(fixed.sum()),
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
            raise ValueError("Changed a protected port, joint, or sharp-edge face")
        area2 = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0],
                                       triangles[:, 2]-triangles[:, 0]), axis=1)
        longest = np.max([np.linalg.norm(triangles[:, a]-triangles[:, b], axis=1)
                          for a, b in ((0, 1), (1, 2), (2, 0))], axis=0)
        altitude = float(np.min(area2/longest))
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
        if (topology["boundary_edges"] or topology["genus"] != 5 or not topology["is_mesh_two_manifold"]
                or topology["connected_components_number"] != 1 or row["zero_area_triangles"]
                or row["self_intersecting_faces"] or row["bounds_mm"] != before["bounds_mm"]):
            raise ValueError(f"Tungsten add-on {label} failed topology, shape, or bounds checks")
    if abs(change) > .01 or max(d["max"] for d in distances) > .05 or altitude < 1e-8:
        raise ValueError("Tungsten add-on decimation failed shape, material, or facet checks")
    report = {NAME: {"original_name": "outer-cone", "before": before, "after": after,
        "repaired_reference": reference, "sampled_distances_mm": distances,
        "decimation_volume_change_percent": change, "protected_faces": int(fixed.sum()),
        "minimum_triangle_altitude_mm": altitude,
        "repair": {"added_port_wall_triangles": 68, "rim_vertices": [33, 35],
            "port_axis": "positive y, inclined 4.5 degrees toward positive z",
            "axis_intercept_z_mm": -124.150890, "nominal_port_radius_mm": 6.35,
            "original_vertices_retained": True, "beam_passage_and_ports_capped": False},
        "mating_surface": {"neighbor": "moller_cone", "neighbor_sha256": MATING_SHA,
            "threshold_mm": .25, "protected_mating_faces": int(mating.sum()),
            "extension_joint_protected_below_z_mm": -169.5},
        "volume_caveat": "The open original has no valid solid volume; changes use the repaired reference."}}
    (Path(output)/"extension_tungsten_mesh_health.json").write_text(json.dumps(report, indent=2)+"\n")
    print(f"{NAME}: {before['triangles']} -> {after['triangles']} triangles; "
          f"volume vs repaired reference {change:.6g}%", flush=True)
