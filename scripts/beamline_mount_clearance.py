#!/usr/bin/env python3
"""Check placed mount/flange collision, containment, and a bound on radial clearance with VTK."""

import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

repo = Path(__file__).resolve().parents[1]
root = repo / "geometry_src/beamline/stls"
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--mount", type=Path, default=root / "FTOuterMount.stl")
parser.add_argument("--flange", type=Path, default=root / "FTOuterFlange.stl")
parser.add_argument("--placements", type=Path, default=repo / "geometry_src/beamline/cad/cad_default.gxml")
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()
rows = {v.get("name"): v.attrib for v in ET.parse(args.placements).getroot().findall("volume")}
mount_row = rows.get("FTOuterMount", rows.get("outerMount"))
flange_row = rows["FTOuterFlange"]
assert mount_row["rotation"] == flange_row["rotation"] == "0*deg 180*deg 0*deg"


def position(row):
    fields = row["position"].split()
    assert all(field.endswith("*mm") for field in fields)
    return np.array([float(field.split("*")[0]) for field in fields])


def load(path, dz=0):
    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(path))
    reader.Update()
    transform = vtk.vtkTransform()
    transform.Translate(0, 0, dz)
    filt = vtk.vtkTransformPolyDataFilter()
    filt.SetTransform(transform)
    filt.SetInputData(reader.GetOutput())
    filt.Update()
    out = vtk.vtkPolyData()
    out.DeepCopy(filt.GetOutput())
    return out


offset = (position(flange_row) - position(mount_row)) * np.array([-1, 1, -1])
assert np.array_equal(offset[:2], [0, 0])
mount = load(args.mount)
flange = load(args.flange, dz=offset[2])
collision = vtk.vtkCollisionDetectionFilter()
identity = vtk.vtkMatrix4x4()
identity.Identity()
for i, poly in enumerate((mount, flange)):
    collision.SetInputData(i, poly)
    collision.SetMatrix(i, identity)
collision.SetCollisionModeToAllContacts()
collision.SetBoxTolerance(0)
collision.SetCellTolerance(1e-8)
collision.Update()
contacts = collision.GetNumberOfContacts()
contained = []
for points, surface in ((mount, flange), (flange, mount)):
    selector = vtk.vtkSelectEnclosedPoints()
    selector.SetInputData(points)
    selector.SetSurfaceData(surface)
    selector.SetTolerance(1e-9)
    selector.Update()
    contained.append(int(vtk_to_numpy(selector.GetOutput().GetPointData().GetArray("SelectedPoints")).sum()))
distance = vtk.vtkDistancePolyDataFilter()
distance.SetInputData(0, mount)
distance.SetInputData(1, flange)
distance.SignedDistanceOff()
distance.Update()
minimum = min(vtk_to_numpy(distance.GetOutput(i).GetPointData().GetArray("Distance")).min() for i in (0, 1))
vv = vtk_to_numpy(mount.GetPoints().GetData()).astype(float)
ff = vtk_to_numpy(mount.GetPolys().GetConnectivityArray()).reshape(-1, 3)
flange_points = vtk_to_numpy(flange.GetPoints().GetData()).astype(float)
end = flange_points[:, 2].max()
samples = [vv[vv[:, 2] <= end]]
for a, b in ((0, 1), (1, 2), (2, 0)):
    x, y = vv[ff[:, a]], vv[ff[:, b]]
    crosses = ((x[:, 2] < end) & (y[:, 2] > end)) | ((x[:, 2] > end) & (y[:, 2] < end))
    x, y = x[crosses], y[crosses]
    samples.append(x + (y-x)*((end-x[:, 2])/(y[:, 2]-x[:, 2]))[:, None])
max_radius = np.linalg.norm(np.vstack(samples)[:, :2], axis=1).max()
ring = flange_points[(flange_points[:, 2] == flange_points[:, 2].min()) &
                     (np.linalg.norm(flange_points[:, :2], axis=1) < 100), :2]
ring = ring[np.argsort(np.arctan2(ring[:, 1], ring[:, 0]))]
following = np.roll(ring, -1, axis=0)
inradius = np.min(abs(ring[:, 0]*following[:, 1]-ring[:, 1]*following[:, 0]) /
                  np.linalg.norm(following-ring, axis=1))
radial_gap = float(inradius-max_radius)
if contacts or contained != [0, 0] or minimum <= 0.02 or radial_gap <= 0.025:
    raise ValueError("Mount/flange collision, containment, or insufficient clearance")
report = {"triangle_contacts": contacts, "contained_vertices": contained,
    "minimum_vertex_to_surface_distance_mm": float(minimum), "radial_clearance_bound_mm": radial_gap,
    "mount_max_radius_in_flange_z_slab_mm": float(max_radius), "flange_inradius_mm": float(inradius),
    "flange_offset_in_mount_mm": offset.tolist(), "vtk_version": vtk.vtkVersion.GetVTKVersion(),
    "mount_sha256": hashlib.sha256(args.mount.read_bytes()).hexdigest(),
    "flange_sha256": hashlib.sha256(args.flange.read_bytes()).hexdigest(),
    "method": "Collision and containment in both directions. Clipped triangle vertices bound the convex "
              "radial norm in the flange z interval. Minimum surface distance samples mesh vertices."}
args.output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report), flush=True)
