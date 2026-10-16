#!/usr/bin/env python3
"""Verify all placed Moller-cone/FT-shield pairs using VTK and clipped-surface radial bounds."""

import argparse
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO/'geometry_src/beamline'))
from moller_cone_mesh import clipped_radius


def load(path, offset):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(path))
    reader.Update()
    transform = vtk.vtkTransform()
    transform.Translate(0, 0, offset)
    filt = vtk.vtkTransformPolyDataFilter()
    filt.SetInputData(reader.GetOutput())
    filt.SetTransform(transform)
    filt.Update()
    out = vtk.vtkPolyData()
    out.DeepCopy(filt.GetOutput())
    return out


def clip(polygon, plane, above):
    result = []
    for a, b in zip(polygon, np.roll(polygon, -1, axis=0)):
        inside_a = a[2] >= plane if above else a[2] <= plane
        inside_b = b[2] >= plane if above else b[2] <= plane
        if inside_a:
            result.append(a)
        if inside_a != inside_b:
            result.append(a+(b-a)*((plane-a[2])/(b[2]-a[2])))
    return np.array(result)


def minimum_projected_radius(vertices, faces, lower, upper):
    minimum = float('inf')
    for triangle in vertices[faces]:
        if triangle[:, 2].max() < lower or triangle[:, 2].min() > upper:
            continue
        polygon = clip(triangle, lower, True)
        if len(polygon):
            polygon = clip(polygon, upper, False)
        if not len(polygon):
            continue
        points = polygon[:, :2]
        following = np.roll(points, -1, axis=0)
        edge = following-points
        length2 = np.square(edge).sum(1)
        weight = np.zeros(len(points))
        valid = length2 > 0
        weight[valid] = np.clip(-(points[valid]*edge[valid]).sum(1)/length2[valid], 0, 1)
        distance = np.linalg.norm(points+weight[:, None]*edge, axis=1).min()
        cross = edge[:, 0]*(-points[:, 1])-edge[:, 1]*(-points[:, 0])
        area = abs((points[:, 0]*following[:, 1]-points[:, 1]*following[:, 0]).sum())
        if area > 1e-10 and (np.all(cross >= -1e-12) or np.all(cross <= 1e-12)):
            distance = 0
        minimum = min(minimum, float(distance))
    return minimum


def check_pair(cone, shield, lower, upper):
    identity = vtk.vtkMatrix4x4()
    identity.Identity()
    collision = vtk.vtkCollisionDetectionFilter()
    for i, poly in enumerate((cone, shield)):
        collision.SetInputData(i, poly)
        collision.SetMatrix(i, identity)
    collision.SetCollisionModeToAllContacts()
    collision.SetBoxTolerance(0)
    collision.SetCellTolerance(1e-8)
    collision.Update()
    contained = []
    for points, surface in ((cone, shield), (shield, cone)):
        selection = vtk.vtkSelectEnclosedPoints()
        selection.SetInputData(points)
        selection.SetSurfaceData(surface)
        selection.SetTolerance(1e-9)
        selection.Update()
        selected = selection.GetOutput().GetPointData().GetArray('SelectedPoints')
        contained.append(int(vtk_to_numpy(selected).sum()))
    distance = vtk.vtkDistancePolyDataFilter()
    distance.SetInputData(0, cone)
    distance.SetInputData(1, shield)
    distance.SignedDistanceOff()
    distance.Update()
    minimum = min(vtk_to_numpy(distance.GetOutput(i).GetPointData().GetArray('Distance')).min() for i in (0, 1))
    cv = vtk_to_numpy(cone.GetPoints().GetData()).astype(float)
    cf = vtk_to_numpy(cone.GetPolys().GetConnectivityArray()).reshape(-1, 3)
    sv = vtk_to_numpy(shield.GetPoints().GetData()).astype(float)
    sf = vtk_to_numpy(shield.GetPolys().GetConnectivityArray()).reshape(-1, 3)
    radial = None
    if upper >= lower:
        cone_radius = minimum_projected_radius(cv, cf, lower, upper)
        shield_radius = clipped_radius(sv, sf, lower, upper)
        radial = {'cone_minimum_surface_radius_mm': cone_radius,
                  'shield_maximum_radius_bound_mm': shield_radius,
                  'radial_separation_bound_mm': cone_radius-shield_radius}
        assert cone_radius-shield_radius > .18
    assert collision.GetNumberOfContacts() == 0 and contained == [0, 0] and minimum > .18
    return {'triangle_contacts': 0, 'contained_vertices': contained,
            'minimum_vertex_to_surface_distance_mm': float(minimum), 'radial_bound': radial}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cone', type=Path, default=REPO/'geometry_src/beamline/stls/moller_cone.stl')
    parser.add_argument('--shield', type=Path, default=REPO/'geometry_src/beamline/stls/FTInnerShield.stl')
    parser.add_argument('--placements', type=Path, default=REPO/'geometry_src/beamline/cad')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    cone = load(args.cone, 0)
    cone_bounds = cone.GetBounds()
    results, groups = {}, {}
    for path in sorted(args.placements.glob('*.gxml')):
        rows = {r.get('name'): r.attrib for r in ET.parse(path).getroot().findall('volume')}
        row = rows.get('moller_cone', rows.get('main-cone'))
        if row is None:
            continue
        shield_row = rows['FTInnerShield']
        assert row['rotation'] == shield_row['rotation'] == '0*deg 180*deg 0*deg'
        cpos = np.array([float(x.removesuffix('*mm')) for x in row['position'].split()])
        spos = np.array([float(x.removesuffix('*mm')) for x in shield_row['position'].split()])
        offset = (spos-cpos)*[-1, 1, -1]
        assert np.array_equal(offset[:2], [0, 0])
        dz = float(offset[2])
        if dz not in groups:
            shield = load(args.shield, dz)
            sb = shield.GetBounds()
            lower, upper = max(cone_bounds[4], sb[4]), min(cone_bounds[5], sb[5])
            groups[dz] = check_pair(cone, shield, lower, upper)
            groups[dz]['shield_offset_in_cone_mm'] = offset.tolist()
            groups[dz]['common_z_interval_mm'] = [lower, upper] if upper >= lower else None
        results[path.stem.removeprefix('cad_')] = groups[dz]
    assert len(results) == 9
    report = {'placements': results, 'vtk_version': vtk.vtkVersion.GetVTKVersion(),
        'cone_sha256': hashlib.sha256(args.cone.read_bytes()).hexdigest(),
        'shield_sha256': hashlib.sha256(args.shield.read_bytes()).hexdigest(),
        'method': 'Collision/containment in both directions; clipped triangle polygons bound surface radii. '
                  'Vertex-to-surface distances are sampled; the radial separation is a geometric bound.'}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(groups), flush=True)


if __name__ == '__main__':
    main()
