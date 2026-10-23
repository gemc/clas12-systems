# HTCC `stls/` CAD meshes

The three cones are CAD rows in the separate SQLite `htcc_cad` system, authored by `build_cad` in
[`../geometry.py`](../geometry.py). Keeping this companion separate preserves the native HTCC comparison
against clas12Tags at 537 geometry rows and eight material rows per configuration. Load both `htcc` and
`htcc_cad` with `factory: sqlite`; the CAD paths are `stls/<name>.stl` relative to the geometry database.

## Placement

The GEMC2 GXML catalogs and GEMC3 Python rows retain the same Rohacell material, names, passive 180-degree
y rotations, and global survey shifts: default 0, rga_spring2018 -10 mm, and rga_fall2018 -19.4 mm.
The Moller-cone extension retains its additional 1 mm z shift. The October 23 repair changes no placement,
material, catalog, or database row.

## Current meshes

Upcoming in the next release: the engineering Moller cone and collar are united into one closed manifold
mesh, resolving `GeomSolids1001` from `G4TessellatedSolid::SetSolidClosed()` in both GEMC engines.
Source and runtime STLs in both repositories are identical. Archived engineering originals remain unchanged.

| Mesh | Engineering facets | Active facets | Components | Boundary edges | Non-manifold edges |
|---|---:|---:|---:|---:|---:|
| htccCone | 18,818 | 6,000 | 2 | 0 | 0 |
| htccMollerCone | 6,232 | 6,902 | 1 | 0 | 0 |
| htccMollerConeExt | 1,748 | 1,748 | 2 | 0 | 0 |

The entry cone and extension are unchanged by this repair. Each retains both shells and its central opening.
The Moller cone is genus one and has no degenerate triangles or detected intersecting faces. Its central bore
and all six engineering bounds remain. The final-to-engineering surface check samples 153,451 points, finding
a maximum distance below 0.000097 mm; sampling does not establish a global distance bound.

The engineering Moller mesh contains two independently closed genus-one pieces sharing a 45-edge seam.
The old generic curing removed part of a 72.5 mm conical section and left non-manifold/intersecting facets.
The dedicated repair starts from the archived engineering export, moves only the collar's shared ring inward
by 0.0001 mm, and forms an exact Boolean union. A 0.0002 mm weld resolves coincident intersection vertices
after binary-STL rounding. Coherent orientation and deterministic face ordering complete the mesh.
There is no Poisson reconstruction, bore capping, or engineering-hole filling.

The new 6,902 facets replace the defective 5,866-facet mesh. Total HTCC CAD facets are now 14,650, versus
26,798 in the engineering exports (45.33% fewer). This repair increases the previous active facet count;
no loading or transport speedup is assigned to it, and no new tracking benchmark was run.

## Reproduction

[`../build_cad_meshes.py`](../build_cad_meshes.py) now reads `clas12Tags/geometry_source/htcc/cad_original/`
instead of reprocessing active meshes. It needs PyMeshLab and pygemc. Rebuild just the repaired mesh with:

```shell
<gemc-dev python_env>/python3 ../build_cad_meshes.py --mesh htccMollerCone
<gemc-dev python_env>/python3 ../build_cad_meshes.py --report
```

Use `--source` and `--output` to override the engineering and destination directories. The dedicated
[`../repair_moller_cone.py`](../repair_moller_cone.py) verifies the input hash, engineering parts, final
manifold topology, unchanged bounds, and retained bore topology. Its health report is
[`moller_cone_mesh_health.json`](moller_cone_mesh_health.json). Repeated builds reproduce the STL and report
byte for byte with the recorded PyMeshLab version. Refresh both repositories' runtime mesh copies afterward.

## Validation limits

The before/after GEMC3 check reproduces the old warning and clears it with the repaired STL. The unchanged
entry cone and extension also pass the direct Geant4 solid checks. Existing entry-cone contact with
`htccEntryWindow`, documented in the CAD optimization note, is separate from this repair and remains.
Construction and surface sampling do not establish detector-response or full tracking equivalence.
