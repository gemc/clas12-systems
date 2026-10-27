# CLAS12 magnets

Upcoming in the next release. This ports the native solenoid and 39 magnets CAD placements from
`clas12Tags/geometry_source/magnets`. The native torus builder is disabled in the reference runner and is
not activated here. Every volume uses passive placement; there is no digitization plugin.

The single SQLite `magnets` system contains the physical `solenoid` volume, 20 CAD sources, and 19 copies.
The solenoid preserves its name, 14 planes, and configuration-dependent z position. CAD sources and copies
retain their GXML names, materials, positions, rotations, colors, and millimetre scale.
Upstream and downstream plates and jackets are optimized separately under
their original names; repeated vacuum jackets use the shared sources described below.
The nine `DSShield*` meshes and `apex` are removed from all three magnets configurations because the
beamline owns this shielding. Load the beamline alongside magnets to include it. This removal reduced the
collection from 148,940 to 132,230 triangles (11.22% fewer), before the plate/jacket optimization below.

The tungsten alloy is defined locally so magnets can run without loading the beamline system.

The six region-1 back membranes and six supports have moved to [DC](../dc/README.md). Load `dc`
to include them; each group uses one STL and five passive copies. Before jacket sharing, magnets had 39 meshes
and 120,622 triangles; DC owns two additional meshes with 1,026 unique triangles for twelve placements.

| Configuration | Run | Solenoid z start (mm) |
|---------------|-----|-----------------------|
| default | 11 | -898.093 |
| rga_spring2018 | 3029 | -900.033 |
| rga_fall2018 | 4763 | -901.093 |

SQLite stores the system under `default`; select a configuration using `runno`. ASCII output retains the
source configuration labels. CAD placements stay at their original positions in all three configurations.

The combined GEMC3 card requires beamline banks at the selected run. The current beamline has no bank at
4763, so that combined configuration omits beamline shielding. Standalone magnets construction passes all
three runs; cross-system run selection remains an existing limitation.

Generate a standalone database from this directory, then construct it with the steering card:

```shell
../../build/subprojects/pygemc/python_env/bin/python3 magnets.py -f sqlite -sql /tmp/magnets.sqlite
gemc magnets.yaml -sql=/tmp/magnets.sqlite -n=0
```

Collect the database and meshes for the experiment steering cards from the repository root:

```shell
./generate_geometry.zsh --no-install
build/subprojects/pygemc/python_env/bin/python3 scripts/compare_ascii_databases.py magnets
```

The comparator checks native geometry and copy rows against the magnets ASCII reference and all CAD placements
against the current GEMC2 GXML. The retained engineering meshes and assembly contacts are unchanged.

## Consolidated detector banks

Upcoming in the next release: `solenoid` is renamed to `magnets` as a geometry bank; the physical volume
remains `solenoid`. GEMC2 folds its 19 `CopyOf` rows into native `magnets` and retains the 20 source meshes
in `magnets_cad`. Its cards load these two factories. GEMC3 keeps all 40 rows in `magnets`, using its SQLite
factory for both native and CAD solids so that copies resolve within the same system.

The separate copy bank is retired. The historical bank names in the studies below describe archived
configurations. No STL, hole, material property, position, or rotation changes in this consolidation.
Magnets retains 66,960 unique facets and 39 CAD placements. No additional simulation speedup is established.

## Downstream plate and vacuum jacket

Upcoming in the next release: `DownstreamShieldingPlate` and `DownstreamVacuumJacket` remain two
separate passive stainless-steel volumes under their original names. Eight plate through-holes and
six blind jacket bolt recesses are filled. Retriangulation retains the main rim coordinates, both
apertures, the hexagonal jacket step, outer bounds, and the 32.83203125 mm axial gap.

The plate has 508 triangles instead of 1,380; the jacket has 556 instead of 2,392. Together they have
1,064 triangles instead of 3,772 (71.79% fewer). Filling the fastener holes increases signed steel
volume by 2.27163% for the plate and 0.46486% for the jacket (0.56658% for the pair). After this downstream
step the magnets collection has 51 meshes and 129,522 triangles.

Rebuild from archived GEMC2 inputs with the mesh-enabled pygemc environment:

```shell
/Users/ungaro/venv/pygemc/bin/python build_cad_meshes.py \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --output /tmp/magnets-plate
```

The output contains both optimized STL files under their original names and mesh-quality metrics.

## Upstream plate and vacuum jacket

Upcoming in the next release: `UpstreamShieldingPlate` and `UpstreamVacuumJacket` retain their
original names and separate passive placements. Eight plate through-holes and six blind jacket bolt
recesses are filled. The plate has 508 rather than 1,380 triangles; the jacket has 1,004 rather
than 2,876 (64.47% fewer together). The original apertures, stepped bore, outer rim and rounded
features, bounds, and 42.87805176 mm axial gap remain. All 894 jacket faces outside the replaced
drilled cap and pocket walls are retained exactly. Signed steel volume increases by 2.27163% for
the plate and 0.52667% for the jacket. Before moving the six DC membranes, magnets had 51 meshes and
126,778 triangles.

```shell
/Users/ungaro/venv/pygemc/bin/python build_cad_meshes.py --pair upstream \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --output /tmp/magnets-upstream
```

## Vacuum jackets

Upcoming in the next release: all jacket names use `vacuumJacket` with sector/side suffixes. The `a` and `b`
jackets have different outlines and holes, so they retain distinct sources. `vacuumJacket2a`,
`vacuumJacket4a`, and `vacuumJacket5a` copy `vacuumJacket`; `vacuumJacket3b`, `vacuumJacket4b`, and
`vacuumJacket6b` copy `vacuumJacket1b`, with exact sector rotations. The four original `vacuumJacket2b`,
`vacuumJacket3a`, `vacuumJacket5b`, and `vacuumJacket6a` meshes remain separate: three preserve
nanometre-sensitive plate contacts, while `vacuumJacket6a` also contains an additional disconnected component.

Every hole, countersink, buried step, and narrow slot is retained. The two optimized source meshes preserve
all protected hole triangles exactly, reducing 8,388 to 8,384 facets and 7,560 to 7,556. The main gain is
sharing: the jacket group falls from 93,726 to 47,934 unique facets (48.86% fewer). All 12 placements remain;
finer canonical tessellations increase placed facets to 95,754. Total signed steel volume changes by
-0.000337%. After jacket sharing, magnets had 33 STL files and 74,830 unique facets for 39 CAD placements.

Export tessellations differ slightly within each family. Fitted circular hole parameters agree within 0.0001
mm; sampled polygonal surfaces differ by up to 0.27 mm. Protected hole geometry is unchanged in the canonical
sources. Dense assembly checks find no new overlap pair with the retained exceptions. Existing assembly
overlaps remain. The consolidation above places the GEMC2 copy rows in native `magnets` alongside the
solenoid; GEMC3 keeps the source meshes and copies together in `magnets`.

```shell
/Users/ungaro/venv/pygemc/bin/python build_vacuum_jackets.py \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --catalogs cad \
  --output /tmp/magnets-vacuum-jackets
```

## Torus coils

Upcoming in the next release: `coil1` becomes `coil`; `coil2` through `coil6` copy its unchanged STL.
All six copper coils match under exact 60-degree sector rotations within 0.000225 mm. Two exports use
the alternate diagonal on one planar side quadrilateral; the boundary and surface are equivalent.
Every opening and all 1,016 canonical facets remain. Removing any contour vertex would change the
profile, so sharing preserves the existing curved surfaces instead of decimating them further.

Unique coil facets fall from 6,096 to 1,016 (83.33% fewer); six placements still contain 6,096 facets.
Signed copper volume changes by -0.000011563%. After coil sharing, magnets had 28 STL files and
69,750 unique facets for 39 CAD placements. GEMC2 then used 28 CAD sources and 11 native `magnets_copies`
rows per run; GEMC3 kept all 39 placements in `magnets_cad`.

The timing study uses `--run-manager Serial --keep-going`. Both tasking and serial attempts encountered
duplicate-isotope registration errors (`PART122`), including with the original geometry. The note reports
completed matched pairs separately and retains every failed run; a complete tracking comparison remains limited.

```shell
/Users/ungaro/venv/pygemc/bin/python build_coils.py \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --catalogs cad --output /tmp/coils
```

## Hub covers

Upcoming in the next release: `Plate1` through `Plate6` become `hubCover1` through `hubCover6`.
The plain `hubCover1` mesh supplies copies 2, 4, and 5; the holed `hubCover3` mesh supplies copy 6.
Both source STLs are unchanged, preserving every surface, the main hole, and all 12 or 150 facets.
Exact sector rotations match the plain covers within 0.00000554 mm and the holed pair within numerical
roundoff. Alternate diagonals on flat faces preserve the same boundaries and surfaces.

Unique cover facets fall from 348 to 162 (53.45% fewer), while six placements retain 348 placed facets.
After hub-cover sharing, magnets had 24 STL sources with 69,564 unique facets for 39 CAD placements.
GEMC2 then used 24 CAD sources and 15 native `magnets_copies` rows per run. Signed aluminum volume is
unchanged to floating-point precision. Original engineering files remain in `cad_original/`.

```shell
/Users/ungaro/venv/pygemc/bin/python build_hub_covers.py \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --catalogs cad --output /tmp/hub-covers
```

## Hub shields

Upcoming in the next release: `Shield2` becomes `hub_shield`, supplying copies `hub_shield3` through
`hub_shield6`. The two different end profiles retain their own meshes as `hub_shield1` and `hub_shield7`.
The five middle exports have identical mapped connectivity and agree within STL rounding after axial
translations. All holes, radial contours, steps, and facet connectivity remain; both end STLs are unchanged.

Recentring the shared mesh reduces axial coordinate rounding. Its far faces shorten by 0.000059326 mm,
avoiding artificial overlaps at the nominal 304.8 mm pitch; final vertices differ from the engineering
placements by at most 0.000146485 mm. Positions retain three decimal places and rotations remain integer.

Unique shield facets fall from 4,146 to 1,594 (61.55% fewer), with 4,146 placed facets across seven volumes.
Signed tungsten-alloy volume changes by -0.000002416%. After hub-shield sharing, magnets had 20 STL sources
and 67,012 unique facets for 39 CAD placements; GEMC2 uses 20 CAD sources and 19 native `magnets`
rows per run.

```shell
/Users/ungaro/venv/pygemc/bin/python build_hub_shields.py \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --catalogs cad --output /tmp/hub-shields
```

## Cold hub

Upcoming in the next release: `Hub001` becomes `ColdHub` in all three configurations and both engines.
Every opening, material, bound, and passive placement remains. Positions use three decimal places.

The mesh closes two microscopic export slivers, reorients 13 faces, and retriangulates seven collinear
junctions without moving their vertices. This removes six boundary edges, seven degenerate triangles,
and eight intersecting faces. The result is one closed manifold component of genus 34.

Conservative edge collapses retain all holes and reduce 12,600 facets to 12,548 (0.41% fewer).
Surviving vertices retain their original coordinates; the largest local plane deviation is 0.000053917 mm.
Bidirectional surface checks sample more than 206,000 points per direction and find deviations below
0.000036 mm. Bounds are unchanged; volume differs from the repaired reference by less than 1e-9%.
Magnets now uses 20 STL sources, 66,960 unique facets, and 39 placements. The original is archived separately.

```shell
/Users/ungaro/venv/pygemc/bin/python build_cold_hub.py \
  --source ../../../clas12Tags/geometry_source/magnets/cad_original --catalogs cad --output /tmp/cold-hub
```

## Bore tubes

Upcoming in the next release: `CenterTube` becomes `BoreCenterTube` in all three configurations and both
engines. `BoreShield` and `WarmBoreTube` retain their names. All three STLs remain byte-identical to their
engineering exports, preserving every profile, bore, bound, and material volume.

The meshes are already closed manifold components of genus one, with no intersecting faces. Every vertex
is a required corner on an inner or outer end rim. Euler's relation gives `F = 2V` for these closed genus-one
triangulations; removing facets would require removing rim corners and changing the profiles.

| Volume | Original facets | Retained facets | Reduction |
|---|---:|---:|---:|
| BoreShield | 356 | 356 | 0% |
| BoreCenterTube | 406 | 406 | 0% |
| WarmBoreTube | 368 | 368 | 0% |
| Total | 1,130 | 1,130 | 0% |

No simulation speedup is established for this unchanged geometry; no new timing benchmark was run.
All nine GEMC3 and GEMC2 SQLite/TEXT construction checks pass for runs 11, 3029, and 4763, and semantic
comparison matches all three CAD configurations. Name-normalized database rows and identical mesh hashes
confirm that the physical placements and clearances are unchanged. Existing assembly overlaps remain.
Magnets still uses 20 STL sources, 66,960 unique facets, and 39 CAD placements.

```shell
/Users/ungaro/venv/pygemc/bin/python audit_bore_tubes.py \
  --originals ../../../clas12Tags/geometry_source/magnets/cad_original --active stls \
  --output /tmp/bore-tube-audit.json
```
