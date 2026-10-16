#!/usr/bin/env python3
"""Optimize selected beamline meshes, retaining bores and sharp engineering features.

Run with the mesh-enabled pygemc environment. Originals are archived in the owning GEMC2 repository;
--source can also point at an untouched checkout's geometry_source/beamline/cad directory.
"""

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pymeshlab as ml

HERE = Path(__file__).resolve().parent
MESHES = {
    "Apex_Shield_Lead_Fill": ("Apex_Shield_Lead_Fill", 1440,
        "1dd10c58dffe8a5075c6697fdc0e7a356937bb813091cdb39fbd208abba00c85"),
    "Apex_Shield_Hub": ("Apex_Shield_PCAL_Hub", 2000,
        "c7472dec10e43fd919cae67fe2db8e255e1ab9e77e337f02598213aaa7b1217c"),
    "Downstream_Beam_tube_Segment_1": ("Downstream_Beam_tube_Segment_1", 5000,
        "c547bf0a7eaca7e106c9ed1a73e1eea88bd7ef4cc52e0f6c0a9d2bb83156ccbb"),
    "Downstream_Beam_tube_Segment_2": ("Downstream_Beam_tube_Segment_2", 600,
        "642b186a0466bcb8993ca74fe2da4d83e62cc9b6ee1200e8b1c773d8cfa9ef49"),
    "Beamline_Adapter_1": ("Torus_Beam_Tube_Reducer_2", 526,
        "e96604bedfb77a7f92bdecde1ff4e843c13004d61899d488d2acea2c8a593a5f"),
    "Torus_Exit_Shield_Casing": ("Torus_Exit_Shield_Casing", 1384,
        "ff322bed2e7180641558d5f916208c2c7779883f3f19380dfc34176c7397ca11"),
    "Torus_Exit_Shield_Lead_Fill": ("Torus_Exit_Shield_Lead_Fill", 384,
        "580e9d1eaa0bf3b22e7d4600b9bc05fa90f9efa08f1562075aad644cf232dc23"),
    "FTInnerShieldAndFlange": ("innerShieldAndFlange", 22000,
        "241ad6089fe618b29bf7213f78681f3cf06df7c5113b5546e9ad3800566d7c6d"),
    "moller_cone_tip": ("cone-tip", 5000,
        "2d31b390fbac29c44ca89dd607c641263658c77eb89a5478ed5de928c09fe5a9"),
    "FTFlange": ("flange-assembly", 540,
        "61c6057a65aed3dcf12efca1b7a88ac36fad74469b80af7f2675ecb4913455bf"),
    "moller-cone-extension-lead-fill": ("lead-shield", 8000,
        "5613bed48c6fb696b98be86c734045af6460904b22ced514a5cde8ccf38bdb88"),
    "moller-cone-extension-lead-case": ("outer-assembly", 10000,
        "c9dfc8a1cc843c22cff112f55b6d238cfb0f2cac6149bc6f1e1a90bbfbd4ab31"),
}
GROUPS = {
    "apex": ("Apex_Shield_Lead_Fill", "Apex_Shield_Hub"),
    "downstream": ("Downstream_Beam_tube_Segment_1", "Downstream_Beam_tube_Segment_2"),
    "exit": ("Beamline_Adapter_1", "Torus_Exit_Shield_Casing", "Torus_Exit_Shield_Lead_Fill"),
    "adjuster": ("ft_adjuster",),
    "inner_shield": ("FTInnerShieldAndFlange",),
    "bolts": tuple(f"FTInnerShieldAndFlange_Bolt{i}" for i in range(1, 10)),
    "outer_flange": ("FTOuterFlange",),
    "outer_mount": ("FTOuterMount",),
    "ft_inner_shield": ("FTInnerShield",),
    "moller_cone": ("moller_cone",),
    "cone_tip": ("moller_cone_tip",),
    "ft_flange": ("FTFlange",),
    "extension_inner": ("moller-cone-extension-inner",),
    "extension_lead": ("moller-cone-extension-lead-fill",),
    "extension_case": ("moller-cone-extension-lead-case",),
    "extension_tungsten": ("moller-cone-extension-tungsten-addon",),
    "ft_joints": ("moller-cone-extension-inner", "moller-cone-extension-lead-case",
                  "moller-cone-extension-lead-fill", "moller-cone-extension-tungsten-addon",
                  "moller_cone", "moller_cone_tip", "FTFlange", "FTInnerShield"),
}
ADJUSTER_HASHES = {
    "adjuster1": "28c7569477c822552a7edb9b90676bb0250fca2a9f26189a264b96ccf6b0cd56",
    "adjuster2": "46d2f910acb1ea1e184fcc6c9f519613004fec94fdc14878d91c5b0b95fbc448",
    "adjuster3": "424deaf268a857b5202403b49cfe0517222f18b637556bcbd27c2abe2535e316",
}


BOLT_HASHES = {
    "nut1": "ce332a69411f308d3869d292ccd94b01c63f31ffeead099fb1c74aa55e5ef9b9",
    "nut2": "391b205d354d6c7e71d446ee9b7d8b3b52f81b3694e134e742d75eca881bb6d8",
    "nut3": "5223e3924ee2fb31a7f81a658b6daea9e2ecb977b36edf338f5e0784e3a5b614",
    "nut4": "0ace2425b0f0efcafafe22331f2127d14399fcc0cd73bd94200cefd7d3a1449c",
    "nut5": "cdbd6772150ce529e94b71cb2bd4934f452ace2455bd0f8cd0b22c59548232c0",
    "nut6": "f9c1663e80df118c0c58f88ca9b9c5786dcdf71fe788b8822538e700de399a6b",
    "nut7": "7814120f683e8bd39a5e1b266bb55ae8763ccd07c5b9bb80c58a4e8fc306221b",
    "nut8": "9b452ec88eb36b0c03cae6b41070a2eaabb147e042a68337d7f8a1d7168a2247",
    "nut9": "25e36f3ede40657c06638e09f86b4da292cd20b757eae4897f7ab9ed9dc70cf2",
}


def sharp_face_quality(mesh, angle=5):
    """Protect faces on edges above the given dihedral angle from edge collapse."""
    vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
    triangles = vertices[faces]
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    owners = np.tile(np.arange(len(faces)), 3)
    order = np.lexsort((edges[:, 1], edges[:, 0]))
    edges, owners = edges[order], owners[order]
    if len(edges) % 2 or not np.all(edges[::2] == edges[1::2]):
        raise ValueError("Expected a closed manifold original mesh")
    sharp = (normals[owners[::2]] * normals[owners[1::2]]).sum(1) < np.cos(np.deg2rad(angle))
    quality = np.ones(len(faces))
    quality[np.concatenate([owners[::2][sharp], owners[1::2][sharp]])] = 0
    return quality


def inventory(path):
    ms = ml.MeshSet()
    ms.load_new_mesh(str(path))
    mesh = ms.current_mesh()
    vertices = mesh.vertex_matrix()
    triangles = vertices[mesh.face_matrix()]
    area = np.linalg.norm(np.cross(triangles[:, 1] - triangles[:, 0],
                                   triangles[:, 2] - triangles[:, 0]), axis=1)
    ms.compute_selection_by_self_intersections_per_face()
    return {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size,
            "triangles": mesh.face_number(), "topology": ms.get_topological_measures(),
            "volume_mm3": ms.get_geometric_measures().get("mesh_volume"),
            "bounds_mm": [vertices.min(0).tolist(), vertices.max(0).tolist()],
            "zero_area_triangles": int(np.count_nonzero(area == 0)),
            "self_intersecting_faces": mesh.selected_face_number()}


def bridge_annular_seams(vertices, faces):
    """Join the seven pairs of concentric boundary rings; never cap the beam passage."""
    edges = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    boundary = unique[counts == 1]
    neighbors = {}
    for a, b in boundary:
        neighbors.setdefault(a, set()).add(b)
        neighbors.setdefault(b, set()).add(a)
    if any(len(adjacent) != 2 for adjacent in neighbors.values()):
        raise ValueError("Expected simple boundary rings")
    groups = {}
    unseen = set(neighbors)
    while unseen:
        pending = [min(unseen)]
        ring = set()
        while pending:
            vertex = pending.pop()
            if vertex not in ring:
                ring.add(vertex)
                pending.extend(neighbors[vertex] - ring)
        unseen -= ring
        ring = np.array(sorted(ring))
        z = vertices[ring, 2]
        if np.ptp(z) > 0.001:
            raise ValueError("Expected coplanar axial boundary rings")
        groups.setdefault(round(float(z.mean()), 3), []).append(ring)
    if len(groups) != 7 or any(len(pair) != 2 for pair in groups.values()):
        raise ValueError("Expected seven annular seam pairs")
    additions = []
    for pair in groups.values():
        pair.sort(key=lambda ids: np.linalg.norm(vertices[ids, :2], axis=1).mean())
        ordered, angles = [], []
        for ring in pair:
            angle = np.mod(np.arctan2(vertices[ring, 1], vertices[ring, 0]), 2 * np.pi)
            ordered.append(ring[np.argsort(angle)])
            angles.append(np.sort(angle))
        a, b = ordered
        aa, bb = angles
        if len(a) != len(b):
            raise ValueError("Expected paired rings with the same angular sampling")
        # The original thin annuli use different angular grids. Register the inner ring to the
        # outer polygon so the repaired join cannot fold across itself; retain every radius and z.
        shift = min(range(len(bb)), key=lambda k:
                    np.square(np.angle(np.exp(1j * (np.roll(bb, -k) - aa)))).sum())
        registered = np.roll(bb, -shift)
        radii = np.linalg.norm(vertices[a, :2], axis=1)
        vertices[a, 0] = radii * np.cos(registered)
        vertices[a, 1] = radii * np.sin(registered)
        a = a[np.argsort(registered)]
        aa = bb.copy()
        i = j = 0
        while i < len(a) or j < len(b):
            next_a = aa[i + 1] if i + 1 < len(a) else aa[0] + 2 * np.pi
            next_b = bb[j + 1] if j + 1 < len(b) else bb[0] + 2 * np.pi
            if i < len(a) and (j == len(b) or next_a < next_b):
                additions.append([a[i % len(a)], a[(i + 1) % len(a)], b[j % len(b)]])
                i += 1
            else:
                additions.append([a[i % len(a)], b[(j + 1) % len(b)], b[j % len(b)]])
                j += 1
    return np.vstack([faces, additions]), np.unique(boundary)


def build_adjuster(source, output):
    """Replace the overlapping adjuster assembly with a prism matched to its sealed union volume."""
    union = ml.MeshSet()
    originals = {}
    for name, expected_hash in ADJUSTER_HASHES.items():
        path = source / (name + ".stl")
        before = inventory(path)
        if before["sha256"] != expected_hash:
            raise ValueError(f"Unexpected original: {path}")
        mesh = ml.MeshSet()
        mesh.load_new_mesh(str(path))
        if before["topology"]["boundary_edges"]:
            # Two original shells lack a nine-edge patch. These caps define a volume reference;
            # their residual intersections are recorded, and none of this geometry is published.
            mesh.meshing_close_holes(maxholesize=16, selfintersection=False)
        mesh.meshing_re_orient_faces_coherently()
        measures = mesh.get_geometric_measures()
        if measures["mesh_volume"] < 0:
            mesh.meshing_invert_face_orientation()
        mesh.compute_selection_by_self_intersections_per_face()
        originals[name] = {"before": before, "sealed_reference_volume_mm3":
            abs(measures["mesh_volume"]), "sealed_reference_topology": mesh.get_topological_measures(),
            "sealed_reference_intersecting_faces": mesh.current_mesh().selected_face_number()}
        union.add_mesh(mesh.current_mesh())
    union.generate_boolean_union(first_mesh=0, second_mesh=1)
    union.generate_boolean_union(first_mesh=union.current_mesh_id(), second_mesh=2)
    measures = union.get_geometric_measures()
    reference_volume = measures["mesh_volume"]
    centre = measures["center_of_mass"]
    lower = min(r["before"]["bounds_mm"][0][2] for r in originals.values())
    upper = max(r["before"]["bounds_mm"][1][2] for r in originals.values())
    length = upper - lower
    sides = 12
    radius = np.sqrt(reference_volume / (0.5 * sides * np.sin(2 * np.pi / sides) * length))
    angles = np.arange(sides) * 2 * np.pi / sides
    vertices = np.array([[centre[0] + radius * np.cos(a), centre[1] + radius * np.sin(a), z]
                         for z in (centre[2] - length / 2, centre[2] + length / 2) for a in angles])
    vertices = np.vstack([vertices, centre + [0, 0, -length / 2], centre + [0, 0, length / 2]])
    faces = []
    for i in range(sides):
        j = (i + 1) % sides
        faces.extend([[i, j, j + sides], [i, j + sides, i + sides],
                      [2 * sides, j, i], [2 * sides + 1, i + sides, j + sides]])
    # Compute normals from the final STL coordinates, eliminating insignificant Boolean-rounding noise.
    vertices = vertices.astype(np.float32).astype(np.float64)
    mesh = ml.MeshSet()
    mesh.add_mesh(ml.Mesh(vertices, np.array(faces)))
    mesh.meshing_re_orient_faces_coherently()
    result = output / "ft_adjuster.stl"
    mesh.save_current_mesh(str(result))
    after = inventory(result)
    relative = 100 * (after["volume_mm3"] / reference_volume - 1)
    topology = after["topology"]
    if (abs(relative) > 0.001 or topology["boundary_edges"] or topology["genus"] != 0
            or topology["connected_components_number"] != 1 or not topology["is_mesh_two_manifold"]
            or after["zero_area_triangles"] or after["self_intersecting_faces"]):
        raise ValueError("ft_adjuster failed material-volume or mesh-quality checks")
    union.compute_selection_by_self_intersections_per_face()
    report = {"originals": originals, "reference_union": {
        "volume_mm3": reference_volume, "centroid_mm": centre.tolist(),
        "topology": union.get_topological_measures(),
        "intersecting_faces": union.current_mesh().selected_face_number(),
        "caveat": "Sealed reference union of imperfect originals; not a certified engineering mass."},
        "after": after, "volume_change_percent": relative,
        "model": {"sides": sides, "radius_mm": radius, "length_mm": length,
                  "centre_mm": centre.tolist(), "shape_preservation_required": False}}
    (output / "adjuster_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"ft_adjuster: 3800 -> {after['triangles']} triangles; volume change {relative:.6g}%", flush=True)


def build_bolts(source, output):
    """Replace threads with smooth solid shafts and round heads, matching each original copper volume."""
    report = {}
    sides = 24
    polygon_area_factor = sides * np.sin(2 * np.pi / sides) / 2
    for i, (original_name, expected_hash) in enumerate(BOLT_HASHES.items(), 1):
        original = source / (original_name + ".stl")
        before = inventory(original)
        if before["sha256"] != expected_hash:
            raise ValueError(f"Unexpected original: {original}")
        ms = ml.MeshSet()
        ms.load_new_mesh(str(original))
        vertices = ms.current_mesh().vertex_matrix()
        centre = (vertices.min(0) + vertices.max(0)) / 2
        axis = 0 if i in (1, 3, 5, 9) else 1
        transverse = [j for j in range(3) if j != axis]
        sign = 1 if centre[axis] > 0 else -1
        axial = sign * vertices[:, axis]
        radial = np.linalg.norm((vertices - centre)[:, transverse], axis=1)
        lower, upper = axial.min(), axial.max()
        # The original tip caps touch the blind-hole end faces. Leave an explicit axial clearance.
        original_lower = lower
        lower += 0.15
        shoulder = axial[radial > 12].min()
        # The old hex head has 28.575 mm across flats. Its inscribed circle stays inside that envelope.
        head_radius = (vertices[:, 2].max() - vertices[:, 2].min()) / 2
        shaft_length, head_length = shoulder - lower, upper - shoulder
        radius = np.sqrt((before["volume_mm3"] / polygon_area_factor -
                          head_radius ** 2 * head_length) / shaft_length)
        if not 7.8 < radius < 9.525:
            raise ValueError("Unexpected smooth shaft radius")
        angles = np.arange(sides) * 2 * np.pi / sides
        rings = [(lower, radius), (shoulder, radius), (shoulder, head_radius), (upper, head_radius)]
        points = []
        for axial_position, ring_radius in rings:
            for angle in angles:
                point = centre.copy()
                point[axis] = sign * axial_position
                point[transverse] += ring_radius * np.array([np.cos(angle), np.sin(angle)])
                points.append(point)
        for axial_position in (lower, upper):
            point = centre.copy()
            point[axis] = sign * axial_position
            points.append(point)
        faces = []
        for ring in range(3):
            for j in range(sides):
                a, b = ring * sides + j, ring * sides + (j + 1) % sides
                faces.extend([[a, b, b + sides], [a, b + sides, a + sides]])
        for j in range(sides):
            k = (j + 1) % sides
            faces.extend([[4 * sides, k, j], [4 * sides + 1, 3 * sides + j, 3 * sides + k]])
        points = np.array(points).astype(np.float32).astype(np.float64)
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(points, np.array(faces)))
        ms.meshing_re_orient_faces_coherently()
        if ms.get_geometric_measures()["mesh_volume"] < 0:
            ms.meshing_invert_face_orientation()
        name = f"FTInnerShieldAndFlange_Bolt{i}"
        result = output / (name + ".stl")
        ms.save_current_mesh(str(result))
        after = inventory(result)
        change = 100 * (after["volume_mm3"] / before["volume_mm3"] - 1)
        topology = after["topology"]
        if (abs(change) > 0.001 or topology["boundary_edges"] or topology["genus"] != 0
                or topology["connected_components_number"] != 1 or not topology["is_mesh_two_manifold"]
                or after["zero_area_triangles"] or after["self_intersecting_faces"]):
            raise ValueError(f"{name}: failed material-volume or quality checks")
        report[name] = {"original_name": original_name, "before": before, "after": after,
            "volume_change_percent": change, "model": {"sides": sides, "axis": axis, "sign": sign,
            "centre_mm": centre.tolist(), "axial_range_mm": [lower, upper], "shoulder_mm": shoulder,
            "original_tip_mm": original_lower, "tip_clearance_mm": 0.15,
            "shaft_radius_mm": radius, "head_radius_mm": head_radius, "hollow": False,
            "threads_retained": False, "shield_clearance_validation_required": True}}
        print(f"{name}: {before['triangles']} -> {after['triangles']} triangles; volume {change:.6g}%",
              flush=True)
    (output / "bolts_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")


def build_outer_flange(source, output):
    """Fill twelve bolt tunnels, then retriangulate the annulus with the exact engineering rim vertices."""
    from tempfile import TemporaryDirectory
    from pygemc.utilities import remove_holes

    original = source / "outerFlange.stl"
    before = inventory(original)
    if before["sha256"] != "ac444ff385c0175ed8c41463cdce499291e967dc8b8c66bc160018e5e10eb7bd":
        raise ValueError("Unexpected outer flange original")
    with TemporaryDirectory() as scratch:
        filled = Path(scratch) / "filled.stl"
        holes = remove_holes(original, filled, max_hole_diameter=40)
        reference = inventory(filled)
        ms = ml.MeshSet()
        ms.load_new_mesh(str(original))
        vertices = ms.current_mesh().vertex_matrix()
        lower, upper = np.unique(vertices[:, 2])
        radii = np.linalg.norm(vertices[:, :2], axis=1)
        rings = []
        top_rings = []
        for radius, expected_count in ((95.25, 97), (127.0, 112)):
            ring = vertices[(vertices[:, 2] == lower) & (abs(radii - radius) < 0.001)]
            angle = np.mod(np.arctan2(ring[:, 1], ring[:, 0]), 2 * np.pi)
            ring = ring[np.argsort(angle)]
            top = vertices[(vertices[:, 2] == upper) & (abs(radii - radius) < 0.001)]
            angle = np.mod(np.arctan2(top[:, 1], top[:, 0]), 2 * np.pi)
            top = top[np.argsort(angle)]
            if len(ring) != expected_count or not np.allclose(ring[:, :2], top[:, :2], rtol=0, atol=1e-10):
                raise ValueError("Unexpected engineering rim coordinates")
            rings.append(ring)
            top_rings.append(top)
        inner, outer = rings
        ni, no = len(inner), len(outer)
        bottom = np.vstack([inner, outer])
        top = np.vstack(top_rings)
        points = np.vstack([bottom, top])
        stride = ni + no
        faces = []
        for start, count in ((0, ni), (ni, no)):
            for i in range(count):
                a, b = start + i, start + (i + 1) % count
                faces.extend([[a, b, b + stride], [a, b + stride, a + stride]])
        angles = [np.mod(np.arctan2(r[:, 1], r[:, 0]), 2 * np.pi) for r in rings]
        i = j = 0
        caps = []
        while i < ni or j < no:
            next_i = angles[0][i + 1] if i + 1 < ni else angles[0][0] + 2 * np.pi
            next_j = angles[1][j + 1] if j + 1 < no else angles[1][0] + 2 * np.pi
            if i < ni and (j == no or next_i < next_j):
                caps.append([i % ni, (i + 1) % ni, ni + j % no])
                i += 1
            else:
                caps.append([i % ni, ni + (j + 1) % no, ni + j % no])
                j += 1
        faces.extend(caps)
        faces.extend([[v + stride for v in face] for face in caps])
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(points, np.array(faces)))
        ms.meshing_re_orient_faces_coherently()
        if ms.get_geometric_measures()["mesh_volume"] < 0:
            ms.meshing_invert_face_orientation()
        result = output / "FTOuterFlange.stl"
        ms.save_current_mesh(str(result))
        after = inventory(result)
        saved = ml.MeshSet()
        saved.load_new_mesh(str(result))
        if set(map(tuple, saved.current_mesh().vertex_matrix())) != set(map(tuple, points)):
            raise ValueError("Changed an engineering flange rim coordinate")
        comparison = ml.MeshSet()
        comparison.load_new_mesh(str(filled))
        comparison.load_new_mesh(str(result))
        distances = [comparison.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
            samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
    change = 100 * (after["volume_mm3"] / before["volume_mm3"] - 1)
    reference_change = 100 * (after["volume_mm3"] / reference["volume_mm3"] - 1)
    topology = after["topology"]
    if (holes["genus_in"] != 13 or holes["genus_out"] != 1 or topology["genus"] != 1
            or topology["boundary_edges"] or not topology["is_mesh_two_manifold"]
            or topology["connected_components_number"] != 1 or after["zero_area_triangles"]
            or after["self_intersecting_faces"] or after["bounds_mm"] != before["bounds_mm"]
            or abs(reference_change) > 0.001 or max(d["max"] for d in distances) > 0.001):
        raise ValueError("FTOuterFlange failed hole-fill, exact-rim, or quality checks")
    report = {"FTOuterFlange": {"original_name": "outerFlange", "before": before, "after": after,
        "hole_fill": holes, "filled_reference": reference, "volume_change_percent": change,
        "retriangulation_volume_change_percent": reference_change, "sampled_distances_mm": distances,
        "model": {"inner_radius_mm": 95.25, "outer_radius_mm": 127.0,
                  "inner_rim_vertices": ni, "outer_rim_vertices": no, "rim_coordinates_retained": True,
                  "closed_bolt_holes": 12, "central_opening_retained": True}}}
    (output / "outer_flange_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"FTOuterFlange: {before['triangles']} -> {after['triangles']} triangles; volume {change:.6g}%",
          flush=True)


def build_outer_mount(source, output):
    """Repair four missing faces and relieve the flange joint before protected mesh simplification."""
    from tempfile import TemporaryDirectory

    original = source / "outerMount.stl"
    flange = HERE / "stls/FTOuterFlange.stl"
    before = inventory(original)
    if before["sha256"] != "12413bd780a2a8a6408e157c756259c155efb4bed1cb6e68d6cd9542f89828e3":
        raise ValueError("Unexpected outer mount original")
    fm = ml.MeshSet()
    fm.load_new_mesh(str(flange))
    fv = fm.current_mesh().vertex_matrix()
    ring = fv[(fv[:, 2] == fv[:, 2].min()) & (np.linalg.norm(fv[:, :2], axis=1) < 100), :2]
    ring = ring[np.argsort(np.arctan2(ring[:, 1], ring[:, 0]))]
    following = np.roll(ring, -1, axis=0)
    inradius = np.min(abs(ring[:, 0]*following[:, 1]-ring[:, 1]*following[:, 0]) /
                      np.linalg.norm(following-ring, axis=1))
    # Passive y=180 placements: the flange's -0.5 mm global z offset is +0.5 mm in mount coordinates.
    joint_end = fv[:, 2].max() + 0.5
    limit = inradius - 0.05
    with TemporaryDirectory() as scratch:
        repaired_path = Path(scratch) / "repaired.stl"
        reference_path = Path(scratch) / "clearance-reference.stl"
        ms = ml.MeshSet()
        ms.load_new_mesh(str(original))
        ms.meshing_close_holes(maxholesize=4, selfintersection=True)
        ms.meshing_re_orient_faces_coherently()
        ms.save_current_mesh(str(repaired_path))
        repaired = inventory(repaired_path)
        if repaired["triangles"] != before["triangles"] + 4 or repaired["topology"]["boundary_edges"]:
            raise ValueError("Expected four triangular surface gaps")
        vertices, faces = ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix()
        radii = np.linalg.norm(vertices[:, :2], axis=1)
        adjusted = (radii > 90) & (vertices[:, 2] < joint_end + 2)
        weights = np.clip((joint_end + 2 - vertices[:, 2]) / 2, 0, 1)
        scale = 1 - weights*(1 - limit/95.25)
        vertices[adjusted, :2] *= scale[adjusted, None]
        vertices = vertices.astype(np.float32).astype(np.float64)
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(vertices, faces))
        ms.meshing_re_orient_faces_coherently()
        ms.save_current_mesh(str(reference_path))
        reference = inventory(reference_path)
        mesh = ms.current_mesh()
        vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
        fixed = (vertices[faces, 2] < joint_end + 2).any(axis=1)
        protected = vertices[faces[fixed]]
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=(~fixed).astype(float)))
        ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=2740-int(fixed.sum()),
            preservenormal=True, preservetopology=True, preserveboundary=True, planarquadric=True,
            autoclean=True, selected=True)
        ms.meshing_re_orient_faces_coherently()
        result = output / "FTOuterMount.stl"
        ms.save_current_mesh(str(result))
        after = inventory(result)
        saved = ml.MeshSet()
        saved.load_new_mesh(str(result))
        mesh = saved.current_mesh()
        saved_faces = {tuple(sorted(map(tuple, t))) for t in mesh.vertex_matrix()[mesh.face_matrix()]}
        if not all(tuple(sorted(map(tuple, t))) in saved_faces for t in protected):
            raise ValueError("Changed a protected flange-joint face")
        comparison = ml.MeshSet()
        comparison.load_new_mesh(str(reference_path))
        comparison.load_new_mesh(str(result))
        distances = [comparison.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
            samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
    change = 100 * (after["volume_mm3"] / repaired["volume_mm3"] - 1)
    decimation_change = 100 * (after["volume_mm3"] / reference["volume_mm3"] - 1)
    topology = after["topology"]
    if (topology["boundary_edges"] or topology["genus"] != repaired["topology"]["genus"]
            or not topology["is_mesh_two_manifold"] or topology["connected_components_number"] != 1
            or after["zero_area_triangles"] or after["self_intersecting_faces"]
            or abs(change) > 0.3 or abs(decimation_change) > 0.005
            or max(d["max"] for d in distances) > 0.05):
        raise ValueError("FTOuterMount failed topology, material, or shape checks")
    report = {"FTOuterMount": {"original_name": "outerMount", "before": before, "after": after,
        "sealed_reference": repaired, "clearance_reference": reference, "volume_change_percent": change,
        "decimation_volume_change_percent": decimation_change, "sampled_distances_mm": distances,
        "flange_sha256": hashlib.sha256(flange.read_bytes()).hexdigest(),
        "repair": {"added_faces": 4, "drilled_holes_filled": False},
        "clearance": {"flange_inradius_mm": inradius, "end_rim_radius_mm": limit,
            "flange_z_offset_in_mount_mm": 0.5, "joint_end_z_mm": joint_end,
            "adjusted_vertices": int(adjusted.sum()), "protected_faces": int(fixed.sum()),
            "surface_and_Geant4_verification_required": True}}}
    (output / "outer_mount_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")
    print(f"FTOuterMount: {before['triangles']} -> {after['triangles']} triangles; volume {change:.6g}%",
          flush=True)


def build(source, output, pair="apex", reference=None, repair_reference=None):
    output.mkdir(parents=True, exist_ok=True)
    if pair == "ft_joints":
        from beamline_joint_mesh import build_joint_clearance
        build_joint_clearance(source, output, reference_output=reference)
        return
    if pair == "extension_tungsten":
        from moller_extension_tungsten_mesh import build_extension_tungsten
        build_extension_tungsten(source, output, reference_output=reference)
        return
    if pair == "extension_inner":
        from moller_extension_inner_mesh import build_extension_inner
        build_extension_inner(source, output, reference_output=reference)
        return
    if pair == "moller_cone":
        from moller_cone_mesh import build_moller_cone
        build_moller_cone(source, output, reference_output=reference, repair_output=repair_reference)
        return
    if pair == "ft_inner_shield":
        from ft_inner_shield_mesh import build_ft_inner_shield
        build_ft_inner_shield(source, output, reference_output=reference)
        return
    if pair == "outer_mount":
        build_outer_mount(source, output)
        return
    if pair == "outer_flange":
        build_outer_flange(source, output)
        return
    if pair == "bolts":
        build_bolts(source, output)
        return
    if pair == "adjuster":
        build_adjuster(source, output)
        return
    report = {}
    for name, (original_name, target, expected_hash) in MESHES.items():
        if name not in GROUPS[pair]:
            continue
        original = source / (original_name + ".stl")
        before = inventory(original)
        if before["sha256"] != expected_hash:
            raise ValueError(f"Unexpected original: {original}")
        ms = ml.MeshSet()
        ms.load_new_mesh(str(original))
        reference_volume = before["volume_mm3"]
        repair = None
        mating_faces = None
        pocket_faces = None
        sharp_faces = None
        if name == "moller_cone_tip" or pair in ("extension_lead", "extension_case"):
            mesh = ms.current_mesh()
            quality = sharp_face_quality(mesh)
            if pair in ("extension_lead", "extension_case"):
                # Retain the complete inner mating surface and its adjacent end faces.
                bore_threshold = 48 if pair == "extension_lead" else 118
                radii = np.linalg.norm(mesh.vertex_matrix()[:, :2], axis=1)
                quality[(radii[mesh.face_matrix()] < bore_threshold).any(axis=1)] = 0
            sharp_faces = mesh.vertex_matrix()[mesh.face_matrix()[quality == 0]]
            target -= len(sharp_faces)
            protected = ml.Mesh(mesh.vertex_matrix(), mesh.face_matrix(), f_scalar_array=quality)
            ms = ml.MeshSet()
            ms.add_mesh(protected)
            ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        if name == "FTInnerShieldAndFlange":
            ms.compute_selection_by_small_disconnected_components_per_face(nbfaceratio=0.02)
            mesh = ms.current_mesh()
            fixed = mesh.face_selection_array()
            if np.count_nonzero(fixed) != 474:
                raise ValueError("Expected the original 474-face enclosed pocket")
            vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
            pocket_faces = vertices[faces[fixed]]
            target -= len(pocket_faces)
            ms = ml.MeshSet()
            ms.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=(~fixed).astype(float)))
            ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        if name == "Torus_Exit_Shield_Casing":
            ms.load_new_mesh(str(source / "Torus_Exit_Shield_Lead_Fill.stl"))
            ms.compute_scalar_by_distance_from_another_mesh_per_vertex(
                measuremesh=0, refmesh=1, signeddist=False)
            ms.set_current_mesh(0)
            mesh = ms.current_mesh()
            vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
            fixed = (mesh.vertex_scalar_array()[faces] < 1.0).any(axis=1)
            mating_faces = vertices[faces[fixed]]
            quality = (~fixed).astype(float)
            target -= int(np.count_nonzero(fixed))
            ms = ml.MeshSet()
            ms.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=quality))
            ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        if name == "Downstream_Beam_tube_Segment_1":
            mesh = ms.current_mesh()
            vertices = mesh.vertex_matrix()
            faces, seam_vertices = bridge_annular_seams(vertices, mesh.face_matrix())
            repaired = ml.Mesh(vertices, faces)
            ms = ml.MeshSet()
            ms.add_mesh(repaired)
            ms.meshing_re_orient_faces_coherently()
            reference_volume = abs(ms.get_geometric_measures()["mesh_volume"])
            repair = {"added_annular_faces": len(faces) - before["triangles"],
                      "reference_volume_mm3": reference_volume, "bores_capped": False}
            mesh = ms.current_mesh()
            quality = np.ones(len(faces))
            quality[np.isin(faces, seam_vertices).any(axis=1)] = 0
            target -= int(np.count_nonzero(quality == 0))
            protected = ml.Mesh(mesh.vertex_matrix(), mesh.face_matrix(), f_scalar_array=quality)
            ms = ml.MeshSet()
            ms.add_mesh(protected)
            ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
            repair["protected_seam_vertices"] = len(seam_vertices)
        if name == "Apex_Shield_Hub":
            mesh = ms.current_mesh()
            protected = ml.Mesh(mesh.vertex_matrix(), mesh.face_matrix(),
                                f_scalar_array=sharp_face_quality(mesh))
            ms = ml.MeshSet()
            ms.add_mesh(protected)
            ms.compute_selection_by_condition_per_face(condselect="fq > 0.5")
        # The hub target applies to selected smooth faces; its 18,000 protected faces remain intact.
        result = output / (name + ".stl")
        if name == "Torus_Exit_Shield_Lead_Fill":
            # This already-clean coarse mesh has tight mating clearances. Even one collapse moves
            # the surface by over 1 mm, so retain the engineering triangulation byte for byte.
            result.write_bytes(original.read_bytes())
        else:
            ms.meshing_decimation_quadric_edge_collapse(
                targetfacenum=target, preservenormal=True, preservetopology=True, preserveboundary=True,
                planarquadric=True, autoclean=True,
                selected=name == "Apex_Shield_Hub" or repair is not None or mating_faces is not None
                or pocket_faces is not None or sharp_faces is not None)
            if name == "FTFlange":
                # Keep the two engineering face planes exact after floating-point edge collapses.
                planes = np.array(before["bounds_mm"])[:, 2]
                mesh = ms.current_mesh()
                vertices = mesh.vertex_matrix()
                faces = mesh.face_matrix()
                vertices[:, 2] = planes[np.argmin(abs(vertices[:, 2, None] - planes), axis=1)]
                ms = ml.MeshSet()
                ms.add_mesh(ml.Mesh(vertices, faces))
            ms.meshing_re_orient_faces_coherently()
            if ms.get_geometric_measures()["mesh_volume"] < 0:
                ms.meshing_invert_face_orientation()
            ms.save_current_mesh(str(result))
        after = inventory(result)
        protected_faces = mating_faces if mating_faces is not None else pocket_faces
        if sharp_faces is not None:
            protected_faces = sharp_faces
        if protected_faces is not None:
            saved = ml.MeshSet()
            saved.load_new_mesh(str(result))
            mesh = saved.current_mesh()
            triangles = {tuple(sorted(map(tuple, t))) for t in mesh.vertex_matrix()[mesh.face_matrix()]}
            if not all(tuple(sorted(map(tuple, t))) in triangles for t in protected_faces):
                raise ValueError(f"{name}: changed a protected face")
        # Measure the saved float32 STL, rather than the in-memory double-precision mesh.
        comparison = ml.MeshSet()
        comparison.load_new_mesh(str(original))
        comparison.load_new_mesh(str(result))
        distances = [comparison.get_hausdorff_distance(
            sampledmesh=a, targetmesh=b, samplenum=100000, samplevert=True,
            sampleedge=True, sampleface=True) for a, b in [(0, 1), (1, 0)]]
        volume_change = 100 * (after["volume_mm3"] / reference_volume - 1)
        for field in ("connected_components_number", "genus", "boundary_edges",
                      "non_two_manifold_edges", "non_two_manifold_vertices"):
            expected = {"connected_components_number": 1, "genus": 1, "boundary_edges": 0,
                        "non_two_manifold_edges": 0, "non_two_manifold_vertices": 0}
            value = expected[field] if repair else before["topology"][field]
            if value != after["topology"][field]:
                raise ValueError(f"{name}: changed {field}")
        limit = {"apex": 0.05, "downstream": 0.5, "exit": 0.51,
                 "inner_shield": 0.05, "cone_tip": 0.05, "ft_flange": 0.05,
                 "extension_lead": 0.05, "extension_case": 0.05}[pair]
        if name.endswith("Segment_1"):
            limit = 0.75
        volume_limit = 0.02 if repair else 0.01
        if (max(d["max"] for d in distances) > limit or abs(volume_change) > volume_limit
                or after["zero_area_triangles"] or after["self_intersecting_faces"]):
            raise ValueError(f"{name}: failed shape/quality checks")
        report[name] = {"original_name": original_name, "before": before, "after": after,
                        "sampled_distances_mm": distances, "volume_change_percent": volume_change,
                        "repair": repair, "sampled_distance_limit_mm": limit}
        if pair == "exit":
            report[name]["protected_mating_faces"] = len(mating_faces) if mating_faces is not None else 0
            report[name]["engineering_bytes_retained"] = name == "Torus_Exit_Shield_Lead_Fill"
        if pocket_faces is not None:
            report[name]["protected_pocket_faces"] = len(pocket_faces)
        if sharp_faces is not None:
            if before["bounds_mm"] != after["bounds_mm"]:
                raise ValueError(f"{name}: changed bounds")
            report[name]["protected_sharp_faces"] = len(sharp_faces)
            report[name]["sharp_edge_threshold_deg"] = 5
            if pair in ("extension_lead", "extension_case"):
                report[name]["protected_bore_radius_threshold_mm"] = bore_threshold
        if name == "FTFlange":
            if before["bounds_mm"] != after["bounds_mm"]:
                raise ValueError("FTFlange: changed engineering bounds")
            report[name]["axial_face_planes_retained_mm"] = planes.tolist()
        print(f"{name}: {before['triangles']} -> {after['triangles']} triangles", flush=True)
    if pair == "downstream":
        from downstream_joint_mesh import relieve_segment_one

        name = "Downstream_Beam_tube_Segment_1"
        row = report[name]
        row["before_joint_relief"] = row["after"]
        row["joint_relief"] = relieve_segment_one(output / (name + ".stl"),
            HERE / "stls/Beamline_Adapter_1.stl", output / "Downstream_Beam_tube_Segment_2.stl")
        row["after"] = inventory(output / (name + ".stl"))
        row["volume_change_vs_previous_percent"] = 100*(
            row["after"]["volume_mm3"] / row["before_joint_relief"]["volume_mm3"]-1)
        row["volume_change_percent"] = 100*(
            row["after"]["volume_mm3"] / row["repair"]["reference_volume_mm3"]-1)
        comparison = ml.MeshSet()
        comparison.load_new_mesh(str(source / (name + ".stl")))
        comparison.load_new_mesh(str(output / (name + ".stl")))
        row["sampled_distances_mm"] = [comparison.get_hausdorff_distance(
            sampledmesh=a, targetmesh=b, samplenum=100000, samplevert=True, sampleedge=True,
            sampleface=True) for a, b in ((0, 1), (1, 0))]
        topology = row["after"]["topology"]
        if (topology["boundary_edges"] or topology["genus"] != 1 or not topology["is_mesh_two_manifold"]
                or topology["connected_components_number"] != 1 or row["after"]["zero_area_triangles"]
                or row["after"]["self_intersecting_faces"]
                or row["after"]["bounds_mm"] != row["before_joint_relief"]["bounds_mm"]
                or abs(row["volume_change_vs_previous_percent"]) > 1
                or max(d["max"] for d in row["sampled_distances_mm"]) > .75):
            raise ValueError("Downstream joint relief failed topology, bounds, volume, or shape checks")
        print(f"{name}: joint relief -> {row['after']['triangles']} final triangles", flush=True)
    (output / f"{pair}_mesh_health.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path,
                        default=HERE.parents[2] / "clas12Tags/geometry_source/beamline/cad_original")
    parser.add_argument("--output", type=Path, default=HERE / "stls")
    parser.add_argument("--pair", choices=tuple(GROUPS), default="apex")
    parser.add_argument("--reference", type=Path,
                        help="Save a shield, cone, or inner-extension reference before decimation")
    parser.add_argument("--repair-reference", type=Path,
                        help="Save the hole-filled Moller cone before counterbore enlargement")
    args = parser.parse_args()
    if args.reference and args.pair not in (
            "ft_inner_shield", "moller_cone", "extension_inner", "extension_tungsten", "ft_joints"):
        parser.error("--reference applies only to shield, cone, or repaired extension groups")
    if args.repair_reference and args.pair != "moller_cone":
        parser.error("--repair-reference applies only to moller_cone")
    build(args.source, args.output, args.pair, reference=args.reference, repair_reference=args.repair_reference)
