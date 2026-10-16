"""Relieve Segment 1's polygonal sockets around the unchanged adapter and Segment 2."""

import hashlib

import numpy as np
import pymeshlab as ml


def slab_points(vertices, faces, lower, upper):
    """Vertices of all triangle portions within a shared axial interval."""
    samples = [vertices[(vertices[:, 2] >= lower) & (vertices[:, 2] <= upper)]]
    for plane in (lower, upper):
        for a, b in ((0, 1), (1, 2), (2, 0)):
            p, q = vertices[faces[:, a]], vertices[faces[:, b]]
            crosses = (p[:, 2]-plane)*(q[:, 2]-plane) < 0
            p, q = p[crosses], q[crosses]
            samples.append(p+(q-p)*((plane-p[:, 2])/(q[:, 2]-p[:, 2]))[:, None])
    return np.vstack(samples)


def relieve_segment_one(path, adapter, segment_two):
    ms = ml.MeshSet()
    ms.load_new_mesh(str(path))
    vertices = ms.current_mesh().vertex_matrix().copy()
    faces = ms.current_mesh().face_matrix().copy()
    report = []
    for neighbor, radius in ((adapter, 60.325), (segment_two, 70.6628)):
        radii = np.linalg.norm(vertices[:, :2], axis=1)
        wall = (abs(radii[faces]-radius) < 1e-4).all(1)
        ids = np.unique(faces[wall])
        levels = sorted(set(vertices[ids, 2]))
        if len(levels) != 2 or wall.sum() != 48:
            raise ValueError('Expected an unchanged 24-sided socket wall')
        bottom, top = [ids[vertices[ids, 2] == level] for level in levels]
        bottom, top = [ring[np.argsort(np.mod(np.arctan2(vertices[ring, 1], vertices[ring, 0]), 2*np.pi))]
                       for ring in (bottom, top)]
        if len(bottom) != 24 or len(top) != 24:
            raise ValueError('Expected paired 24-vertex socket rings')
        polygon = vertices[bottom, :2]
        edges = np.roll(polygon, -1, axis=0)-polygon
        normals = np.column_stack([edges[:, 1], -edges[:, 0]])
        normals /= np.linalg.norm(normals, axis=1)[:, None]
        offsets = (normals*polygon).sum(1)
        other = ml.MeshSet()
        other.load_new_mesh(str(neighbor))
        nv, nf = other.current_mesh().vertex_matrix(), other.current_mesh().face_matrix()
        lower = max(vertices[:, 2].min(), nv[:, 2].min())
        upper = min(vertices[:, 2].max(), nv[:, 2].max())
        samples = slab_points(nv, nf, lower, upper)
        support = (samples[:, :2]@normals.T).max(0)
        # A small numerical margin beyond the 0.1 mm face clearance protects float32 output.
        scale = float(((support+.10002)/offsets).max())
        if neighbor == adapter:
            vertices[bottom, :2] *= scale
            additions, rings = [], [bottom]
            for z, factor in ((upper+.1, scale), (upper+1.1, 1)):
                ring = vertices[bottom].copy()
                ring[:, :2] *= factor/scale
                ring[:, 2] = z
                rings.append(np.arange(len(vertices), len(vertices)+24))
                vertices = np.vstack([vertices, ring])
            rings.append(top)
            for a, b in zip(rings, rings[1:]):
                for i in range(24):
                    j = (i+1) % 24
                    additions.extend([[a[i], b[j], a[j]], [a[i], b[i], b[j]]])
            faces = np.vstack([faces[~wall], additions])
        else:
            vertices[ids, :2] *= scale
        report.append({'neighbor': neighbor.stem,
            'neighbor_sha256': hashlib.sha256(neighbor.read_bytes()).hexdigest(),
            'scale': scale, 'radius_before_mm': radius, 'radius_after_mm': radius*scale,
            'common_z_mm': [float(lower), float(upper)],
            'old_minimum_support_gap_mm': float((offsets-support).min()), 'design_normal_gap_mm': .1})
    ms = ml.MeshSet()
    ms.add_mesh(ml.Mesh(vertices, faces))
    ms.meshing_re_orient_faces_coherently()
    ms.save_current_mesh(str(path))
    return report
