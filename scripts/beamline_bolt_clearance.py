#!/usr/bin/env python3
"""Validate smooth FT bolt clearance with VTK in the mesh-enabled environment."""

from pathlib import Path
import hashlib
import json
import argparse
import vtk
from vtk.util.numpy_support import vtk_to_numpy

parser = argparse.ArgumentParser(description="Check bolt surfaces and containment against the FT shield.")
parser.add_argument("--meshes", type=Path,
                    default=Path(__file__).resolve().parents[1] / "geometry_src/beamline/stls")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
root = args.meshes

def load(path):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(path))
    reader.Update()
    poly = vtk.vtkPolyData()
    poly.DeepCopy(reader.GetOutput())
    return poly

def contained(points, surface):
    selector = vtk.vtkSelectEnclosedPoints()
    selector.SetInputData(points)
    selector.SetSurfaceData(surface)
    selector.SetTolerance(1e-8)
    selector.Update()
    return int(vtk_to_numpy(selector.GetOutput().GetPointData().GetArray('SelectedPoints')).sum())

shield_path = root / 'FTInnerShieldAndFlange.stl'
shield = load(shield_path)
report = {'shield_sha256': hashlib.sha256(shield_path.read_bytes()).hexdigest(), 'bolts': {}}
for i in range(1, 10):
    name = f'FTInnerShieldAndFlange_Bolt{i}'
    path = root / (name + '.stl')
    bolt = load(path)
    collision = vtk.vtkCollisionDetectionFilter()
    identity = vtk.vtkMatrix4x4()
    identity.Identity()
    collision.SetInputData(0, bolt)
    collision.SetInputData(1, shield)
    collision.SetMatrix(0, identity)
    collision.SetMatrix(1, identity)
    collision.SetCollisionModeToAllContacts()
    collision.SetBoxTolerance(0)
    collision.SetCellTolerance(1e-6)
    collision.Update()
    contacts = collision.GetNumberOfContacts()
    if contacts:
        points = vtk_to_numpy(collision.GetContactsOutput().GetPoints().GetData())
        print('contact bounds', points.min(0), points.max(0), flush=True)
    bolt_inside = contained(bolt, shield)
    shield_inside = contained(shield, bolt)
    distance = vtk.vtkDistancePolyDataFilter()
    distance.SetInputData(0, bolt)
    distance.SetInputData(1, shield)
    distance.SignedDistanceOff()
    distance.Update()
    minimum = min(vtk_to_numpy(distance.GetOutput(port).GetPointData().GetArray('Distance')).min()
                  for port in (0, 1))
    row = {'triangle_contacts': contacts, 'bolt_vertices_inside_shield': bolt_inside,
           'shield_vertices_inside_bolt': shield_inside,
           'minimum_bidirectional_vertex_to_surface_distance_mm': float(minimum),
           'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    print(name, row, flush=True)
    if contacts or bolt_inside or shield_inside or minimum <= 0.1:
        raise ValueError(f'{name}: shield intersection or insufficient sampled clearance')
    report['bolts'][name] = row
report['method'] = ('VTK triangle collision plus enclosed-point checks in both directions; identical '
                    'CAD transforms permit comparisons in STL coordinates. Distances sample vertices, '
                    'not a certified global surface clearance.')
args.output.write_text(json.dumps(report, indent=2) + '\n')
