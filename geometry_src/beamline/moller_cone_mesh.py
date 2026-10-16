"""Fill cone surface openings and enlarge its counterbore around the placed FT inner shield."""

from collections import defaultdict
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import xml.etree.ElementTree as ET

import numpy as np
import pymeshlab as ml

HERE = Path(__file__).resolve().parent


def clipped_radius(vertices, faces, lower, upper):
    """Bound the radial norm of all triangle portions within an axial slab."""
    samples = [vertices[(vertices[:, 2] >= lower) & (vertices[:, 2] <= upper)]]
    for plane in (lower, upper):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            x, y = vertices[faces[:, a]], vertices[faces[:, b]]
            crosses = ((x[:, 2] < plane) & (y[:, 2] > plane)) | ((x[:, 2] > plane) & (y[:, 2] < plane))
            x, y = x[crosses], y[crosses]
            samples.append(x+(y-x)*((plane-x[:, 2])/(y[:, 2]-x[:, 2]))[:, None])
    points = np.vstack(samples)
    return float(np.linalg.norm(points[:, :2], axis=1).max()) if len(points) else 0


def joint_parameters(cone_bounds):
    shield_path = HERE/'stls/FTInnerShield.stl'
    ms = ml.MeshSet()
    ms.load_new_mesh(str(shield_path))
    v, f = ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix()
    placements = []
    for p in sorted((HERE/'cad').glob('*.gxml')):
        rows = {r.get('name'): r.attrib for r in ET.parse(p).getroot().findall('volume')}
        cone = rows.get('moller_cone', rows.get('main-cone'))
        if cone is None:
            continue
        shield = rows['FTInnerShield']
        assert cone['rotation'] == shield['rotation'] == '0*deg 180*deg 0*deg'
        positions = [np.array([float(x.removesuffix('*mm')) for x in row['position'].split()])
                     for row in (cone, shield)]
        offset = (positions[1]-positions[0])*[-1, 1, -1]
        assert np.array_equal(offset[:2], [0, 0])
        overlapping = v[:, 2].max()+offset[2] >= cone_bounds[0][2]
        radius = clipped_radius(v, f, cone_bounds[0][2]-offset[2], cone_bounds[1][2]-offset[2])
        placements.append({'variation': p.stem.removeprefix('cad_'), 'cone_position_mm': positions[0].tolist(),
            'shield_offset_in_cone_mm': offset.tolist(), 'axial_overlap': bool(overlapping),
            'shield_radius_bound_mm': radius, 'shield_tip_z_in_cone_mm': float(v[:, 2].max()+offset[2])})
    assert len(placements) == 9
    relevant = [row for row in placements if row['axial_overlap']]
    radius = max(row['shield_radius_bound_mm'] for row in relevant)+0.2
    end = max(row['shield_tip_z_in_cone_mm'] for row in relevant)+0.2
    return radius, end, placements, hashlib.sha256(shield_path.read_bytes()).hexdigest()


def fill_surface_openings(vertices, faces):
    edges = np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]])
    _, inverse, counts = np.unique(np.sort(edges, axis=1), axis=0, return_inverse=True, return_counts=True)
    boundary = edges[counts[inverse] == 1]
    adjacency = defaultdict(set)
    for a, b in boundary:
        adjacency[int(a)].add(int(b))
        adjacency[int(b)].add(int(a))
    if len(boundary) != 302 or any(len(neighbors) != 2 for neighbors in adjacency.values()):
        raise ValueError('Expected eight simple source surface openings')
    unseen, groups = set(adjacency), []
    while unseen:
        pending, group = [min(unseen)], set()
        while pending:
            i = pending.pop()
            if i not in group:
                group.add(i)
                pending.extend(adjacency[i]-group)
        unseen -= group
        groups.append(sorted(group))
    if len(groups) != 8:
        raise ValueError('Expected eight source boundary loops')

    def radius(z, outer):
        if not outer:
            return 39.98595 if z < -55.232959 else 34.975
        if z < -55.232959:
            return 76.05+(71.03-76.05)*(z+170.632965)/115.400006
        return -0.0428580417*z+68.6628228

    def project(point, outer):
        point = point.copy()
        point[:2] *= radius(point[2], outer)/np.linalg.norm(point[:2])
        return point

    points, additions, report = vertices.tolist(), [], []
    for group in groups:
        centre = vertices[group].mean(0)
        outer = np.linalg.norm(centre[:2]) > radius(centre[2], True)-2
        centre = project(centre, outer)
        centre_id = len(points)
        points.append(centre.tolist())
        middle = {}
        for i in group:
            middle[i] = len(points)
            points.append(project((vertices[i]+centre)/2, outer).tolist())
        group_set = set(group)
        for a, b in boundary:
            if a in group_set:
                additions.extend([[b, a, middle[a]], [b, middle[a], middle[b]],
                                  [middle[b], middle[a], centre_id]])
        report.append({'boundary_vertices': len(group), 'outer': bool(outer), 'centre_mm': centre.tolist()})
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(np.array(points), np.vstack([faces, additions])))
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()['mesh_volume'] < 0:
        ms.meshing_invert_face_orientation()
    return ms, report


def bore_cutter(radius, lower, upper, sides=128):
    angles = np.arange(sides)*2*np.pi/sides
    points = np.array([[radius*np.cos(a), radius*np.sin(a), z] for z in (lower, upper) for a in angles])
    points = np.vstack([points, [0, 0, lower], [0, 0, upper]])
    faces = []
    for i in range(sides):
        j = (i+1)%sides
        faces.extend([[i, j, j+sides], [i, j+sides, i+sides],
                      [2*sides, j, i], [2*sides+1, i+sides, j+sides]])
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(points, np.array(faces)))
    ms.meshing_re_orient_faces_coherently()
    if ms.get_geometric_measures()['mesh_volume'] < 0:
        ms.meshing_invert_face_orientation()
    return ms


def build_moller_cone(source, output, reference_output=None, repair_output=None):
    from build_cad_meshes import inventory, sharp_face_quality

    before = inventory(source/'main-cone.stl')
    if before['sha256'] != '7340c0b4fe9d0640e95860dce5f3c702487ef43d1cb733ad6c0d9e499c64671e':
        raise ValueError('Unexpected original Moller cone')
    radius, end, placements, shield_hash = joint_parameters(before['bounds_mm'])
    with TemporaryDirectory() as scratch:
        repaired_path = Path(scratch)/'hole-filled-reference.stl'
        reference_path = Path(scratch)/'clearance-reference.stl'
        original = ml.MeshSet()
        original.load_new_mesh(str(source/'main-cone.stl'))
        mesh = original.current_mesh()
        ms, holes = fill_surface_openings(mesh.vertex_matrix(), mesh.face_matrix())
        ms.save_current_mesh(str(repaired_path))
        repaired = inventory(repaired_path)
        cutter = bore_cutter(radius, before['bounds_mm'][0][2]-1, end)
        ms = ml.MeshSet()
        ms.load_new_mesh(str(repaired_path))
        ms.add_mesh(cutter.current_mesh())
        ms.generate_boolean_difference(first_mesh=0, second_mesh=1)
        ms.meshing_merge_close_vertices(threshold=ml.PureValue(1e-6))
        ms.meshing_remove_duplicate_faces()
        ms.meshing_remove_null_faces()
        ms.meshing_remove_unreferenced_vertices()
        ms.meshing_re_orient_faces_coherently()
        ms.save_current_mesh(str(reference_path))
        reference = inventory(reference_path)
        ms = ml.MeshSet()
        ms.load_new_mesh(str(reference_path))
        v, f = ms.current_mesh().vertex_matrix(), ms.current_mesh().face_matrix()
        t = v[f]
        fixed = ((np.linalg.norm(t[:, :, :2], axis=2) < radius+0.4) & (t[:, :, 2] < end+1e-4)).any(1)
        fixed |= sharp_face_quality(ms.current_mesh(), angle=20) == 0
        protected = t[fixed]
        ms = ml.MeshSet()
        ms.add_mesh(ml.Mesh(v, f, f_scalar_array=(~fixed).astype(float)))
        ms.compute_selection_by_condition_per_face(condselect='fq > 0.5')
        ms.meshing_decimation_quadric_edge_collapse(targetfacenum=5000-int(fixed.sum()),
            preservenormal=True, preservetopology=True, preserveboundary=True, planarquadric=True,
            autoclean=True, selected=True)
        ms.meshing_re_orient_faces_coherently()
        result = output/'moller_cone.stl'
        ms.save_current_mesh(str(result))
        after = inventory(result)
        saved = ml.MeshSet()
        saved.load_new_mesh(str(result))
        mesh = saved.current_mesh()
        triangles = mesh.vertex_matrix()[mesh.face_matrix()]
        saved_faces = {tuple(sorted(map(tuple, face))) for face in triangles}
        if not all(tuple(sorted(map(tuple, face))) in saved_faces for face in protected):
            raise ValueError('Changed a protected counterbore or corner face')
        area = np.linalg.norm(np.cross(triangles[:, 1]-triangles[:, 0],
                                        triangles[:, 2]-triangles[:, 0]), axis=1)
        longest = np.max([np.linalg.norm(triangles[:, a]-triangles[:, b], axis=1)
                          for a, b in ((0, 1), (1, 2), (2, 0))], axis=0)
        altitude = float((area/longest).min())
        compare = ml.MeshSet()
        compare.load_new_mesh(str(reference_path))
        compare.load_new_mesh(str(result))
        distances = [compare.get_hausdorff_distance(sampledmesh=a, targetmesh=b, samplenum=100000,
            samplevert=True, sampleedge=True, sampleface=True) for a, b in ((0, 1), (1, 0))]
        for destination, path in ((repair_output, repaired_path), (reference_output, reference_path)):
            if destination is not None:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(path.read_bytes())
    change = 100*(after['volume_mm3']/reference['volume_mm3']-1)
    topology = after['topology']
    if (topology['boundary_edges'] or topology['genus'] != 1 or not topology['is_mesh_two_manifold']
            or topology['connected_components_number'] != 1 or after['zero_area_triangles']
            or after['self_intersecting_faces'] or after['bounds_mm'] != before['bounds_mm']
            or altitude < 1e-8 or abs(change) > .005 or max(d['max'] for d in distances) > .05):
        raise ValueError('Moller cone failed topology, bounds, shape, or facet-quality checks')
    report = {'moller_cone': {'original_name': 'main-cone', 'before': before, 'after': after,
        'hole_filled_reference': repaired, 'clearance_reference': reference, 'hole_repairs': holes,
        'protected_faces': int(fixed.sum()), 'minimum_triangle_altitude_mm': altitude,
        'sampled_distances_mm': distances, 'decimation_volume_change_percent': change,
        'volume_change_vs_hole_filled_percent': 100*(after['volume_mm3']/repaired['volume_mm3']-1),
        'joint': {'counterbore_radius_mm': radius, 'counterbore_end_z_mm': end, 'sides': 128,
            'radial_design_gap_mm': .2, 'axial_design_gap_mm': .2, 'shield_sha256': shield_hash,
            'placements': placements, 'surface_and_Geant4_checks_required': True},
        'original_volume_caveat':
            'The original surface is open; material comparison uses the repaired reference.'}}
    (output/'moller_cone_mesh_health.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f"moller_cone: {before['triangles']} -> {after['triangles']} triangles; "
          f"counterbore radius {radius:.6f} mm, end z {end:.6f} mm", flush=True)
