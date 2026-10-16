"""Relieve the placed FT/cone joints using archived optimized inputs and local material removal."""

import json
import struct
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pymeshlab as ml

ARCHIVE = "ft_joint_inputs_20261016"
NAMES = (
    "moller-cone-extension-inner", "moller-cone-extension-lead-case", "moller-cone-extension-lead-fill",
    "moller-cone-extension-tungsten-addon", "moller_cone", "moller_cone_tip", "FTFlange", "FTInnerShield",
)
INPUT_HASHES = {'FTFlange': '8682f9792b4c060a205c73716d281834b57c3b0107735e207e22fde25aa54c74',
 'FTInnerShield': '0d770b71801eb4c9167c57d325314eb3ac11995431335532fe8828906b48a82a',
 'moller-cone-extension-inner': '2a84ad71756d5d2dcd2cba42958fb7719fba3c78746d9901007f4e1163bf9637',
 'moller-cone-extension-lead-case': '6da8aaa2f4ef20cc5e6b25e3c97247044c7c21d6aaec53f5e6897fac4ad9cd11',
 'moller-cone-extension-lead-fill': 'ea95201f26dfeeeb6799418cff3dfec97def974fcff8b963d0aecff828ffccd2',
 'moller-cone-extension-tungsten-addon': 'c01cf671cbda10ad96eca519c1d42edfdf92b77fdf24a75b8f34c81a1e855ea8',
 'moller_cone': '6640a8179f48d30242da0fafcc7c4f4c1be97022a73c4d94e0291221dcae96e0',
 'moller_cone_tip': '67382ae73d760a7f2d8ca8a3c79b53710930540227e45ae9c492ecf59902483f'}


def clean(meshes, tolerance):
    meshes.meshing_merge_close_vertices(threshold=ml.PureValue(tolerance))
    meshes.meshing_remove_duplicate_faces()
    meshes.meshing_remove_null_faces()
    meshes.meshing_remove_unreferenced_vertices()
    meshes.meshing_re_orient_faces_coherently()


def canonical_stl(path):
    """Normalize facet order and discard null facets without changing coordinates or winding."""
    raw = path.read_bytes()
    dtype = np.dtype([("normal", "<f4", 3), ("vertices", "<f4", (3, 3)), ("attribute", "<u2")])
    triangles = np.frombuffer(raw, dtype=dtype, offset=84)["vertices"].copy()
    first = np.lexsort((triangles[:, :, 2], triangles[:, :, 1], triangles[:, :, 0]), axis=1)[:, 0]
    indices = (first[:, None]+np.arange(3)) % 3
    triangles = np.take_along_axis(triangles, indices[:, :, None], axis=1)
    flat = triangles.reshape(-1, 9)
    triangles = triangles[np.lexsort(tuple(flat[:, i] for i in range(8, -1, -1)))]
    points = triangles.astype(float)
    normals = np.cross(points[:, 1]-points[:, 0], points[:, 2]-points[:, 0])
    lengths = np.linalg.norm(normals, axis=1)
    valid = lengths > 0
    triangles, normals = triangles[valid], normals[valid]/lengths[valid, None]
    records = np.zeros(len(triangles), dtype=dtype)
    records["vertices"], records["normal"] = triangles, normals
    header = b"CLAS12 beamline joint clearance".ljust(80, b"\0")
    path.write_bytes(header+struct.pack("<I", len(records))+records.tobytes())


def profile(rows, sides=128):
    """Build a filled cutter whose polygon faces enclose the specified circular profile."""
    angles = np.arange(sides)*2*np.pi/sides
    vertices = np.array([[r/np.cos(np.pi/sides)*np.cos(a), r/np.cos(np.pi/sides)*np.sin(a), z]
                         for z, r in rows for a in angles])
    vertices = np.vstack([vertices, [0, 0, rows[0][0]], [0, 0, rows[-1][0]]])
    faces = []
    for k in range(len(rows)-1):
        for i in range(sides):
            j = (i+1) % sides
            a, b, c, d = k*sides+i, k*sides+j, (k+1)*sides+i, (k+1)*sides+j
            faces.extend([[a, b, c], [b, d, c]])
    for i in range(sides):
        j = (i+1) % sides
        faces.extend([[len(rows)*sides, j, i],
                      [len(rows)*sides+1, (len(rows)-1)*sides+i, (len(rows)-1)*sides+j]])
    meshes = ml.MeshSet()
    meshes.add_mesh(ml.Mesh(vertices, np.array(faces)))
    meshes.meshing_re_orient_faces_coherently()
    if meshes.get_geometric_measures()["mesh_volume"] < 0:
        meshes.meshing_invert_face_orientation()
    return meshes


def operate(original, operations, result):
    meshes = ml.MeshSet()
    meshes.load_new_mesh(str(original))
    for operation, cutter in operations:
        current = meshes.current_mesh_id()
        meshes.add_mesh(cutter.current_mesh())
        getattr(meshes, "generate_boolean_"+operation)(first_mesh=current, second_mesh=meshes.current_mesh_id())
        clean(meshes, 1e-6)
    meshes.save_current_mesh(str(result))


def flange_bore_bound(vertices, faces):
    minimum = float("inf")
    for triangle in vertices[faces, :2]:
        following = np.roll(triangle, -1, axis=0)
        edges = following-triangle
        length2 = np.square(edges).sum(1)
        weight = np.zeros(3)
        valid = length2 > 0
        weight[valid] = np.clip(-(triangle[valid]*edges[valid]).sum(1)/length2[valid], 0, 1)
        minimum = min(minimum, float(np.linalg.norm(triangle+weight[:, None]*edges, axis=1).min()))
        cross = edges[:, 0]*(-triangle[:, 1])-edges[:, 1]*(-triangle[:, 0])
        area = abs((triangle[:, 0]*following[:, 1]-triangle[:, 1]*following[:, 0]).sum())
        if area > 1e-10 and (np.all(cross >= -1e-12) or np.all(cross <= 1e-12)):
            raise ValueError("Unexpected triangle across the FT flange bore")
    return minimum


def retessellate_upper_cap(meshes):
    """Use an angular strip for the planar end face, retaining its exact boundary and surface."""
    mesh = meshes.current_mesh()
    v, f = mesh.vertex_matrix(), mesh.face_matrix()
    cap = (v[f, 2] == float(np.float32(711.95))).all(axis=1)
    cf = f[cap]
    edges = np.sort(np.concatenate([cf[:, [0, 1]], cf[:, [1, 2]], cf[:, [2, 0]]]), axis=1)
    unique, counts = np.unique(edges, axis=0, return_counts=True)
    adjacency = {}
    for a, b in unique[counts == 1]:
        adjacency.setdefault(int(a), set()).add(int(b))
        adjacency.setdefault(int(b), set()).add(int(a))
    if any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError("Expected simple planar end-face boundary rings")
    unseen, loops = set(adjacency), []
    while unseen:
        start = min(unseen)
        current, previous, ring = start, None, []
        while current not in ring:
            ring.append(current)
            choices = adjacency[current]-({previous} if previous is not None else set())
            previous, current = current, min(choices)
        if current != start:
            raise ValueError("Unexpected end-face boundary branching")
        unseen -= set(ring)
        loops.append(np.array(ring))
    if len(loops) != 2:
        raise ValueError("Expected the annular end face")
    loops.sort(key=lambda ring: np.linalg.norm(v[ring, :2], axis=1).mean())
    angles = []
    for k, ring in enumerate(loops):
        angle = np.mod(np.arctan2(v[ring, 1], v[ring, 0]), 2*np.pi)
        order = np.argsort(angle)
        loops[k] = ring[order]
        angles.append(angle[order])
    a, b = loops
    aa, bb = angles
    i, j, extra = 0, 0, []
    while i < len(a) or j < len(b):
        next_a = aa[i+1] if i+1 < len(a) else aa[0]+2*np.pi
        next_b = bb[j+1] if j+1 < len(b) else bb[0]+2*np.pi
        if i < len(a) and (j == len(b) or next_a < next_b):
            extra.append([a[i % len(a)], a[(i+1) % len(a)], b[j % len(b)]])
            i += 1
        else:
            extra.append([a[i % len(a)], b[(j+1) % len(b)], b[j % len(b)]])
            j += 1
    new = np.array(extra)
    triangles = v[new]
    flip = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])[:, 2] < 0
    new[flip] = new[flip][:, [0, 2, 1]]
    meshes = ml.MeshSet()
    meshes.add_mesh(ml.Mesh(v, np.vstack([f[~cap], new])))
    meshes.meshing_remove_unreferenced_vertices()
    meshes.meshing_re_orient_faces_coherently()
    return meshes


def build_joint_clearance(source, output, reference_output=None):
    from build_cad_meshes import inventory, sharp_face_quality

    source = Path(source)
    if (source/ARCHIVE).is_dir():
        source = source/ARCHIVE
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    before = {name: inventory(source/(name+".stl")) for name in NAMES}
    if {name: row["sha256"] for name, row in before.items()} != INPUT_HASHES:
        raise ValueError("Joint clearance requires the archived pre-clearance optimized meshes")
    for name in NAMES:
        (output/(name+".stl")).write_bytes((source/(name+".stl")).read_bytes())
    flange = ml.MeshSet()
    flange.load_new_mesh(str(source/"FTFlange.stl"))
    mesh = flange.current_mesh()
    fv, ff = mesh.vertex_matrix(), mesh.face_matrix()
    limit = flange_bore_bound(fv, ff)-.03
    inner_profile = [(-527, limit*np.cos(np.pi/128)), (-519.94, limit*np.cos(np.pi/128)),
                     (-519.84, 60), (0, 60)]
    operate(source/(NAMES[0]+".stl"), [
        ("difference", profile([(-527, 40.05), (-369.63, 40.05)])),
        ("intersection", profile(inner_profile)),
    ], output/(NAMES[0]+".stl"))
    operate(source/(NAMES[2]+".stl"), [
        ("difference", profile([(-521, 47.68), (-169, 47.68)])),
    ], output/(NAMES[2]+".stl"))
    main_bore = [(-171, 47.725), (-170.58, 47.725), (-170.48, 41.65), (-169.7, 41.65),
                 (-169.4, 40.30), (-53.43, 40.30)]
    tip_bore = [(639.369, 35.075), (711.522, 35.075), (711.903, 35.456), (713, 35.456)]
    operate(source/"moller_cone.stl", [
        ("difference", profile(main_bore)), ("difference", profile(tip_bore)),
        ("intersection", profile([(-172, 100), (711.95, 100)], sides=32)),
    ], output/"moller_cone.stl")

    def cone_radius(z):
        if z < -55.232959:
            return 76.05+(71.03-76.05)*(z+170.632965)/115.400006
        return -.0428580417*z+68.6628228

    addon_profile = [(z, cone_radius(z)+.10) for z in (-170.833, -55.232959, 113.894)]
    operate(source/(NAMES[3]+".stl"), [("difference", profile(addon_profile))], output/(NAMES[3]+".stl"))
    hull = ml.MeshSet()
    hull.load_new_mesh(str(source/(NAMES[2]+".stl")))
    hull.generate_convex_hull()
    hull.meshing_re_orient_faces_coherently()
    if hull.get_geometric_measures()["mesh_volume"] < 0:
        hull.meshing_invert_face_orientation()
    mesh = hull.current_mesh()
    vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
    centre = np.array([0, 0, (vertices[:, 2].min()+vertices[:, 2].max())/2])
    triangles = vertices[faces]
    normals = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    offsets = ((triangles[:, 0]-centre)*normals).sum(1)
    if offsets.min() <= 0:
        raise ValueError("Unexpected convex envelope orientation")
    scale = 1+.02002/offsets.min()
    hull = ml.MeshSet()
    hull.add_mesh(ml.Mesh(centre+(vertices-centre)*scale, faces))
    flange_radius = np.linalg.norm(fv[:, :2], axis=1).max()+.02002
    case = output/(NAMES[1]+".stl")
    operate(source/case.name, [("difference", hull), ("difference", profile(
        [(-524, flange_radius), (fv[:, 2].max()+.02002, flange_radius)], sides=256))], case)
    with TemporaryDirectory() as scratch:
        reference = Path(scratch)/"case-reference.stl"
        reference.write_bytes(case.read_bytes())
        archive_reference = Path(scratch)/"canonical-case-reference.stl"
        archive_reference.write_bytes(reference.read_bytes())
        canonical_stl(archive_reference)
        case_reference = inventory(archive_reference)
        if reference_output is not None:
            reference_output.parent.mkdir(parents=True, exist_ok=True)
            reference_output.write_bytes(archive_reference.read_bytes())
        meshes = ml.MeshSet()
        meshes.load_new_mesh(str(reference))
        clean(meshes, .001)
        mesh = meshes.current_mesh()
        vertices, faces = mesh.vertex_matrix(), mesh.face_matrix()
        quality = sharp_face_quality(mesh, angle=5)
        fixed = int((quality == 0).sum())
        meshes = ml.MeshSet()
        meshes.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=quality))
        meshes.compute_selection_by_condition_per_face(condselect="fq > .5")
        meshes.meshing_decimation_quadric_edge_collapse(targetfacenum=16000-fixed, preservenormal=True,
            preservetopology=True, preserveboundary=True, planarquadric=True, autoclean=True,
            selected=True, optimalplacement=False)
        meshes.save_current_mesh(str(case))
        # Reload float32 output before the final weld; Geant4/CADMesh also reads these stored coordinates.
        report = {}
        limits = dict(zip(NAMES[:5], [1, 1.5, .3, .5, .2]))
        for name in NAMES[:5]:
            result = output/(name+".stl")
            meshes = ml.MeshSet()
            meshes.load_new_mesh(str(result))
            clean(meshes, 1e-4)
            if name == "moller_cone":
                meshes = retessellate_upper_cap(meshes)
            meshes.save_current_mesh(str(result))
            canonical_stl(result)
            after = inventory(result)
            topology = after["topology"]
            change = 100*(after["volume_mm3"]/before[name]["volume_mm3"]-1)
            if (not topology["is_mesh_two_manifold"] or topology["boundary_edges"]
                    or topology["connected_components_number"] != 1
                    or topology["genus"] != before[name]["topology"]["genus"]
                    or after["self_intersecting_faces"] or after["zero_area_triangles"]
                    or change > 1e-6 or change < -limits[name]):
                raise ValueError(f"Joint correction failed topology or material guard: {name}")
            compare = ml.MeshSet()
            compare.load_new_mesh(str(source/result.name))
            compare.load_new_mesh(str(result))
            distances = [compare.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
                samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
            report[name] = {"before": before[name], "after": after, "volume_change_percent": change,
                            "sampled_distances_mm": distances}
        compare = ml.MeshSet()
        compare.load_new_mesh(str(reference))
        compare.load_new_mesh(str(case))
        distances = [compare.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
            samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
        change = 100*(report[NAMES[1]]["after"]["volume_mm3"]/case_reference["volume_mm3"]-1)
        if max(row["max"] for row in distances) > .01 or abs(change) > .005:
            raise ValueError("Case simplification changed the relieved surface excessively")
    health = {"meshes": report, "input_sha256": INPUT_HASHES, "archive": ARCHIVE,
        "fixed_meshes": list(NAMES[5:]), "case_boolean_reference": case_reference,
        "case_decimation": {"sampled_distances_mm": distances, "volume_change_percent": change,
                            "weld_before_decimation_mm": .001, "sharp_angle_deg": 5},
        "final_float32_weld_mm": .0001,
        "upper_cap_retriangulation": "Angular annular strip at local z=711.95 mm; geometry unchanged",
        "operations": {"inner_bore": [[-527, 40.05], [-369.63, 40.05]],
            "inner_flange_outer_radius_limit_mm": limit, "main_bore_profile_z_r_mm": main_bore,
            "tip_bore_profile_z_r_mm": tip_bore, "main_upper_face_z_mm": 711.95,
            "addon_bore_profile_z_r_mm": addon_profile, "case_envelope_scale": float(scale),
            "case_envelope_minimum_plane_gap_mm": .02002, "case_flange_radius_mm": float(flange_radius)},
        "placement_caveat": "The FT shield is offset -369.73 mm in the common passive cone frame."}
    (output/"ft_joints_mesh_health.json").write_text(json.dumps(health, indent=2)+"\n")
    reports = dict(zip(NAMES[:5], ("extension_inner", "extension_case", "extension_lead",
                                  "extension_tungsten", "moller_cone")))
    for name, stem in reports.items():
        path = source/(stem+"_mesh_health.json")
        if path.exists():
            previous = json.loads(path.read_text())[name]
            updated = {"original_name": previous["original_name"], "before": previous["before"],
                "after": report[name]["after"], "previous_optimization": previous,
                "joint_clearance": {"report": "ft_joints_mesh_health.json", **report[name]},
                "scope": "Previous optimization measurements precede the local clearance corrections."}
            (output/path.name).write_text(json.dumps({name: updated}, indent=2)+"\n")
    print("Corrected five joint meshes; preserved the FT shield, FT flange, and cone tip.", flush=True)
