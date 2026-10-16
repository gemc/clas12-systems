#!/usr/bin/env python3
"""Check downstream joints with triangle collisions, containment, and socket-plane clearances."""

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
from downstream_joint_mesh import slab_points


def load(path):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(path))
    reader.Update()
    return reader.GetOutput()


def arrays(poly):
    return (vtk_to_numpy(poly.GetPoints().GetData()).astype(float),
            vtk_to_numpy(poly.GetPolys().GetConnectivityArray()).reshape(-1, 3))


def check_pair(female, male, radius):
    identity = vtk.vtkMatrix4x4()
    identity.Identity()
    collision = vtk.vtkCollisionDetectionFilter()
    for i, poly in enumerate((female, male)):
        collision.SetInputData(i, poly)
        collision.SetMatrix(i, identity)
    collision.SetCollisionModeToAllContacts()
    collision.SetBoxTolerance(0)
    collision.SetCellTolerance(1e-8)
    collision.Update()
    contained = []
    for points, surface in ((female, male), (male, female)):
        selection = vtk.vtkSelectEnclosedPoints()
        selection.SetInputData(points)
        selection.SetSurfaceData(surface)
        selection.SetTolerance(1e-9)
        selection.Update()
        selected = selection.GetOutput().GetPointData().GetArray('SelectedPoints')
        contained.append(int(vtk_to_numpy(selected).sum()))
    fv, ff = arrays(female)
    mv, mf = arrays(male)
    triangles = fv[ff[(abs(np.linalg.norm(fv[:, :2], axis=1)[ff]-radius) < 1e-4).all(1)]]
    assert len(triangles) == 48
    normals = np.cross(triangles[:, 1]-triangles[:, 0], triangles[:, 2]-triangles[:, 0])
    normals /= np.linalg.norm(normals, axis=1)[:, None]
    normals[(normals[:, :2]*triangles[:, :, :2].mean(1)).sum(1) < 0] *= -1
    lower, upper = max(fv[:, 2].min(), mv[:, 2].min()), min(fv[:, 2].max(), mv[:, 2].max())
    samples = slab_points(mv, mf, lower, upper)
    gaps = (normals*triangles[:, 0]).sum(1)-(samples@normals.T).max(0)
    assert not collision.GetNumberOfContacts() and contained == [0, 0] and gaps.min() > .0999
    return {'triangle_contacts': 0, 'contained_vertices': contained,
            'minimum_socket_plane_clearance_mm': float(gaps.min()),
            'common_z_mm': [float(lower), float(upper)], 'socket_triangles_checked': len(triangles)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--meshes', type=Path, default=REPO/'geometry_src/beamline/stls')
    parser.add_argument('--placements', type=Path, default=REPO/'geometry_src/beamline/cad')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    name = 'Downstream_Beam_tube_Segment_1'
    health = json.loads((args.meshes/'downstream_mesh_health.json').read_text())[name]
    female = load(args.meshes/(name+'.stl'))
    report = {'pairs': {}, 'mesh_hashes': {}, 'variations': [], 'vtk_version': vtk.vtkVersion.GetVTKVersion()}
    for row in health['joint_relief']:
        neighbor = row['neighbor']
        path = args.meshes/(neighbor+'.stl')
        report['pairs'][neighbor] = check_pair(female, load(path), row['radius_after_mm'])
        report['mesh_hashes'][neighbor] = hashlib.sha256(path.read_bytes()).hexdigest()
    report['mesh_hashes'][name] = hashlib.sha256((args.meshes/(name+'.stl')).read_bytes()).hexdigest()
    for path in sorted(args.placements.glob('*.gxml')):
        rows = {row.get('name'): row.attrib for row in ET.parse(path).getroot().findall('volume')}
        if name in rows:
            for part in report['mesh_hashes']:
                assert rows[part].get('position', '0*mm 0*mm 0*mm') == '0*mm 0*mm 0*mm'
                assert rows[part].get('rotation', '0*deg 0*deg 0*deg') == '0*deg 0*deg 0*deg'
            report['variations'].append(path.stem.removeprefix('cad_'))
    assert len(report['variations']) == 11
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report['pairs']), flush=True)


if __name__ == '__main__':
    main()
