"""Rebuild the damaged FT inner shield, retaining its longitudinal grooves and smoothing the flange."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np
import pymeshlab as ml


def revolved(n=128):
    # Cross-section of the engineering tube, chamfers, fillets, and 20 mm flange.
    profile = [(30, 0), (30, -665), (34.5, -665), (36, -663.5), (36, -635), (40, -635), (40, -630)]
    profile += [(45-5*np.cos(a), -630+5*np.sin(a)) for a in np.linspace(0, np.pi/2, 9)[1:]]
    profile += [(100, -625), (100, -605), (50, -605)]
    profile += [(50-10*np.sin(a), -595-10*np.cos(a)) for a in np.linspace(0, np.pi/2, 13)[1:]]
    profile += [(40, -2), (38, 0)]
    angles = np.arange(n)*2*np.pi/n
    vertices = np.array([[r*np.cos(a), r*np.sin(a), z] for r, z in profile for a in angles])
    faces = []
    for k in range(len(profile)):
        q = (k+1)%len(profile)
        for i in range(n):
            j = (i+1)%n
            a, b, c, d = k*n+i, k*n+j, q*n+i, q*n+j
            faces.extend([[a, b, d], [a, d, c]])
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertices, np.array(faces)))
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()['mesh_volume'] < 0:
        ms.meshing_invert_face_orientation()
    return ms


def groove(angle):
    centre = -575+np.sqrt(27)
    zs = np.r_[np.linspace(-575, centre, 17), 2]
    floor = np.r_[43-np.sqrt(36-(zs[:-1]-centre)**2), 37]
    contour = np.c_[floor, zs].tolist()+[[50, 2], [50, -575]]
    # The epigraph of this convex end profile has simple fan caps on both extrusion faces.
    vertices = np.array([[h, t, z] for t in (-3, 3) for h, z in contour])
    n = len(contour)
    faces = []
    for i in range(n):
        j = (i+1)%n
        faces.extend([[i, j, j+n], [i, j+n, i+n]])
    for i in range(1, n-1):
        faces.extend([[0, i, i+1], [n, n+i+1, n+i]])
    a = np.deg2rad(angle)
    x, y = vertices[:, 0].copy(), vertices[:, 1].copy()
    vertices[:, 0] = x*np.cos(a)-y*np.sin(a)
    vertices[:, 1] = x*np.sin(a)+y*np.cos(a)
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertices, np.array(faces)))
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()['mesh_volume'] < 0:
        ms.meshing_invert_face_orientation()
    return ms


def feature_mask(vertices, faces):
    from build_cad_meshes import sharp_face_quality

    triangles = vertices[faces]
    fixed = np.zeros(len(faces), bool)
    for z in (-625, -605):
        fixed |= np.isclose(triangles[:, :, 2], z, rtol=0, atol=1e-6).all(1)
    for angle in np.deg2rad([45, 135]):
        height = triangles[:, :, 0]*np.cos(angle)+triangles[:, :, 1]*np.sin(angle)
        width = -triangles[:, :, 0]*np.sin(angle)+triangles[:, :, 1]*np.cos(angle)
        fixed |= ((height > 36.9) & (height < 40.1) & (abs(width) < 3.01)
                  & (triangles[:, :, 2] > -575.01)).all(1)
    fixed |= sharp_face_quality(ml.Mesh(vertices, faces), angle=15) == 0
    return fixed


def build_ft_inner_shield(source, output, reference_output=None):
    from build_cad_meshes import inventory

    original = source / 'taggerInnerShield.stl'
    before = inventory(original)
    if before['sha256'] != '29f15d29ac5e1a09adf2bc7fb0fa0cc4d539f3567f2fdd92c084b9f3be56fbe1':
        raise ValueError('Unexpected FT inner-shield engineering mesh')
    with TemporaryDirectory() as scratch:
        reference_path = Path(scratch) / 'filled-reference.stl'
        ms = revolved()
        for angle in (45, 135):
            index = ms.current_mesh_id()
            cutter = groove(angle)
            ms.add_mesh(cutter.current_mesh())
            ms.generate_boolean_difference(first_mesh=index, second_mesh=ms.current_mesh_id())
        # Exact-axis trigonometric rounding can leave duplicate vertices separated by 1e-15 mm.
        # Geant4 rejects their sliver facets even when MeshLab reports a closed manifold surface.
        ms.meshing_merge_close_vertices(threshold=ml.PureValue(1e-6))
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_null_faces()
        ms.meshing_remove_unreferenced_vertices()
        ms.meshing_re_orient_faces_coherently()
        ms.save_current_mesh(str(reference_path))
        reference = inventory(reference_path)
        # Boolean outputs can have near-coincident coordinates; reload the actual saved surface.
        ms = ml.MeshSet()
        ms.load_new_mesh(str(reference_path))
        vertices, faces = ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix()
        fixed = feature_mask(vertices, faces)
        protected = vertices[faces[fixed]]
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(vertices, faces, f_scalar_array=(~fixed).astype(float)))
        ms.compute_selection_by_condition_per_face(condselect='fq > 0.5')
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=6500-int(fixed.sum()),
            preservenormal=True, preservetopology=True, preserveboundary=True, planarquadric=True,
            autoclean=True, selected=True)
        ms.meshing_re_orient_faces_coherently()
        result = output / 'FTInnerShield.stl'
        ms.save_current_mesh(str(result))
        after = inventory(result)
        saved = ml.MeshSet()
        saved.load_new_mesh(str(result))
        mesh = saved.current_mesh()
        triangles = mesh.vertex_matrix()[mesh.face_matrix()]
        cross = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0],
                                        triangles[:, 2]-triangles[:, 0]), axis=1)
        longest = np.max([np.linalg.norm(triangles[:, a]-triangles[:, b], axis=1)
                          for a, b in ((0, 1), (1, 2), (2, 0))], axis=0)
        minimum_altitude = float(np.min(cross/longest))
        saved_faces = {tuple(sorted(map(tuple, t))) for t in mesh.vertex_matrix()[mesh.face_matrix()]}
        if not all(tuple(sorted(map(tuple, t))) in saved_faces for t in protected):
            raise ValueError('Changed a protected groove, flat flange face, or engineering corner')
        compare = ml.MeshSet()
        compare.load_new_mesh(str(reference_path))
        compare.load_new_mesh(str(result))
        distances = [compare.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
            samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
        # Preserve the reference for fixed-material tracking controls and independent review.
        if reference_output is not None:
            reference_output.parent.mkdir(parents=True, exist_ok=True)
            reference_output.write_bytes(reference_path.read_bytes())
    change = 100*(after['volume_mm3']/reference['volume_mm3']-1)
    topology = after['topology']
    if (topology['boundary_edges'] or topology['genus'] != 1 or not topology['is_mesh_two_manifold']
            or topology['connected_components_number'] != 1 or after['zero_area_triangles']
            or after['self_intersecting_faces'] or after['bounds_mm'] != reference['bounds_mm']
            or minimum_altitude < 1e-8 or abs(change) > .005
            or max(d['max'] for d in distances) > .05):
        raise ValueError('FTInnerShield failed profile, topology, or protected-decimation checks')
    report = {'FTInnerShield': {'original_name': 'taggerInnerShield', 'before': before, 'after': after,
        'rebuilt_reference': reference, 'decimation_volume_change_percent': change,
        'sampled_distances_mm': distances, 'protected_faces': int(fixed.sum()),
        'minimum_triangle_altitude_mm': minimum_altitude, 'boolean_weld_tolerance_mm': 1e-6,
        'model': {'tube_inner_radius_mm': 30, 'tube_outer_radius_mm': 40, 'length_mm': 665,
            'flange_radius_mm': 100, 'flange_z_mm': [-625, -605], 'angular_segments': 128,
            'longitudinal_grooves': 2, 'groove_width_mm': 6, 'groove_depth_mm': 3,
            'groove_end_radius_mm': 6, 'groove_start_z_mm': -575, 'groove_end_z_mm': 0,
            'flange_through_holes_closed': 26, 'tube_through_holes_closed': 1,
            'conical_recesses': 0, 'face_chamfers': 0, 'stepped_counterbores': 0,
            'flange_surfaces_smooth': True, 'central_passage_retained': True},
        'volume_caveat': 'Original is open and non-manifold; original solid volume is undefined.'}}
    (output / 'ft_inner_shield_mesh_health.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"FTInnerShield: {before['triangles']} -> {after['triangles']} triangles; "
          f"protected-decimation volume change {change:.6g}%", flush=True)
