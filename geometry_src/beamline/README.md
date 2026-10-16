# CLAS12 beamline

Upcoming in the next release. This is the beamline import from
`clas12Tags/geometry_source/beamline`. The native builder follows the current `beamline.pl` dispatch:
`vacuumLine.pl`, `ELMOline.pl`, `rghline.pl`, `transverseUpstreamBeampipe.pl`, `ddvcsTungstenCone.pl`, and
`highLumi.pl`. Historical files that are no longer called, and disabled HD-ice daughters, are not activated.
All published volumes use passive placement. There is no sensitive digitization plugin or optical surface.

The original CAD placements are retained as GXML under `cad/` and `cad_transverse/`, with attributes wrapped
for readability. The 49 STL files under `stls/` comprise 28 beamline meshes and seven meshes for each of
`noWedges`, `forwardWedges`, and `midpointWedges`. Twenty-seven assets have reduced triangulations as described
below; the other 22 retain their original bytes. The exit-shield lead fill was evaluated and retained exactly to
preserve its tight casing clearances. STEP files and the reference image are not runtime inputs.

## Apex mesh optimization

`Apex_Shield_Lead_Fill` is reduced from 2,880 to 1,440 triangles. `Apex_Shield_PCAL_Hub` is renamed
`Apex_Shield_Hub` and reduced from 36,354 to 20,000 triangles. Topology-preserving quadric decimation
retains the lead opening and both hub components. Hub faces adjoining edges above five degrees are protected.
No holes are filled, components removed, surfaces reconstructed, or placements/materials changed.

The saved meshes remain closed, manifold, outward oriented, and free of detected self-intersections and
zero-area triangles. Bidirectional vertex, edge, and surface sampling measures deviations below 0.05 mm;
this is a sampled measurement, not a proven global error bound. `stls/apex_mesh_health.json` records the
original/output hashes, topology, bounds, volumes, and sampled distances. Originals are retained under
`clas12Tags/geometry_source/beamline/cad_original/`.

Regenerate with a Python environment containing NumPy and PyMeshLab:

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py
```

The offline benchmark isolates this pair with identical materials and fixed 5 GeV primaries from the target
over 0.25--3.5 degrees, no magnetic field, FTFP_BERT, one thread, and no GUI or event output:

```shell
python3 scripts/beamline_cad_benchmark.py --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/apex-benchmark --events 200 --repeats 5
```

It alternates case order, retains all input files/logs and executable/STL hashes, and separately records
loading, electron/proton/pion/neutron transport, peak memory, and construction overlap diagnostics. Results
belong to this isolated workload and do not establish complete CLAS12 performance or response equivalence.

## Downstream tube optimization

`Downstream_Beam_tube_Segment_1` is repaired and reduced from 5,146 to 5,096 triangles, including the
socket clearance revision described below. Its original surface has 392
boundary edges, seven disconnected components, and 1,021 detected intersecting faces. Seven missing annular
joins are bridged with 392 faces before decimation; their angular tessellation is registered while preserving
the measured radii and axial positions. Seam vertices are protected during decimation. The beam passage
remains open. The result is one closed,
manifold tube with genus one, no detected self-intersections, and no zero-area triangles. Generic hole filling
would cap the bore and is deliberately avoided.

`Downstream_Beam_tube_Segment_2` remains a closed, manifold tube and is reduced from 672 to 600 triangles.
Names, materials, coordinate frames, and placements are unchanged. These already-coarse meshes permit modest
reductions: sampled maximum surface deviations are 0.746 mm and 0.457 mm, mainly at connector/flange features.
Bounds change by at most 0.011 mm. The apex's 0.05 mm sampled limit does not apply to this pair.

`stls/downstream_mesh_health.json` records topology, hashes, distances, and volume changes. Segment 1 has no
well-defined original volume because its surface is open; decimation and socket relief change the
annularly repaired reference volume by -0.620987%. Segment 2 changes by -0.00170%. These are mesh checks,
not response equivalence.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair downstream
python3 scripts/beamline_cad_benchmark.py --pair downstream --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/downstream-benchmark --events 200 --repeats 5
```

The downstream benchmark uses fixed 5 GeV primaries over 0.1--1.3 degrees, all azimuths, and the same physics,
thread count, alternating case order, and separate loading/transport/overlap measurements as the apex test.
The archived originals include both downstream meshes. Remaining pair overlaps are measured separately;
mesh repair alone does not change the engineering placements.

## Adapter and torus exit shield

`Torus_Beam_Tube_Reducer_2` is renamed `Beamline_Adapter_1` in every CAD variation and reduced from 528 to
526 triangles. `Torus_Exit_Shield_Casing` is reduced from 1,392 to 1,384 triangles. These engineering meshes
are already coarse, so reductions are deliberately small. The casing's 432 faces with a vertex within
1 mm of the lead fill are protected and verified to retain exactly the same vertex coordinates.
`Torus_Exit_Shield_Lead_Fill` is already clean at 384 triangles; it is retained byte for byte because even
one trial edge collapse displaced its surface by more than 1 mm near tight mating clearances.

All three retain their components, genus, closed manifold topology, bounds, materials, and placements.
No self-intersections or zero-area faces are detected. Maximum bidirectionally sampled deviations are
0.456 mm for the adapter and 0.5002 mm for the casing, below this group's 0.51 mm sampling guard; this is
not a proven global bound or the apex's 0.05 mm criterion. Volume changes are +0.000368% and +0.000188%.
The group decreases from 2,304 to 2,294 triangles (0.434%) and from 115,452 to 114,952 bytes.
`stls/exit_mesh_health.json` records the checks and the lead fill's retained original hash.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair exit
python3 scripts/beamline_cad_benchmark.py --pair exit --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/exit-benchmark --events 200 --repeats 5
```

The isolated three-volume benchmark uses matched 5 GeV primaries over 0.25--2.6 degrees and full azimuth.
Loading, transport, memory, and overlap diagnostics are retained separately. Given the small triangle
reduction, timing fluctuations must not be interpreted as substantial performance gains.

## FT adjuster material model

`adjuster1`, `adjuster2`, and `adjuster3` are replaced by one `ft_adjuster` STL and one CAD placement in
all nine variations that contain the trio. Their common `G4_STAINLESS-STEEL` material, passive transform,
and color are retained. Shape detail is deliberately simplified in favor of the amount of material.
The result is a closed 12-sided prism with 48 triangles instead of 3,800 (98.74% fewer), with its axis
through the reference union's centroid and the same 152.370 mm longitudinal span.

Two originals have nine-edge surface openings. Small patches establish a sealed reference before Boolean
union; their residual intersections are recorded, and that reference geometry is not published. The sealed
parts sum to 25,203.967 mm3; overlap removal gives a reference union of 24,922.570 mm3. Independent
inclusion-exclusion of the pairwise intersection volumes agrees within 0.00001%. This defines an estimated
material budget, not a certified engineering mass or response-equivalent shape. The final saved STL differs
from that union volume by -0.0000284%, has one closed manifold component with genus zero, and has no detected
self-intersections or zero-area faces. Original STLs are retained in `cad_original/` in clas12Tags.

`stls/adjuster_mesh_health.json` retains original hashes, reference defects, the material budget, and output
checks. The benchmark reconstructs either the original three CAD rows or their one-row replacement from
the common physical attributes, so it accepts a generated database from either state:

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair adjuster
python3 scripts/beamline_cad_benchmark.py --pair adjuster --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/adjuster-benchmark --events 200 --repeats 5
```

The matched 5 GeV primaries cover 2.5--3.3 degrees and azimuths -95-- -85 degrees, directed toward the
off-axis adjuster. Loading, peak memory, transport, and overlap diagnostics are retained separately.
The replacement redistributes material and changes navigation; timing gains do not prove unchanged response.

## FT inner shield and flange

`innerShieldAndFlange` is renamed `FTInnerShieldAndFlange` in all ten applicable CAD variations and reduced
from 34,448 to 22,000 triangles (36.14% fewer). The tungsten-alloy material, common passive placement,
coordinate frame, and overall bounds are unchanged. Topology-preserving decimation retains the two closed
manifold surface components and aggregate genus 17, including the bore and mounting holes. The small
inward-oriented enclosed pocket is protected: all 474 of its original triangles remain at exactly the
same coordinates. No holes are filled, components removed, or surfaces reconstructed.

Maximum bidirectional vertex/edge/surface sampling gives a 0.0481 mm deviation, below the 0.05 mm guard.
This is a sampled maximum, not a proven global error bound. Total signed volume changes by -0.0000439%;
a separate component calculation confirms the pocket is unchanged and the main component changes by
-0.0000411%. The saved STL has no detected self-intersections or zero-area faces.
`stls/inner_shield_mesh_health.json` records hashes, topology, bounds, volumes, and sampled distances.
The original is retained under `clas12Tags/geometry_source/beamline/cad_original/`.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair inner_shield
python3 scripts/beamline_cad_benchmark.py --pair inner_shield --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/inner-shield-benchmark --events 200 --repeats 5
```

The isolated one-mesh benchmark uses matched 5 GeV primaries over 0.25--3.0 degrees and full azimuth,
with the same physics and separate loading, transport, memory, and overlap diagnostics as earlier studies.
Its metadata and raw results are retained in the CAD optimization note; full-experiment performance and
response equivalence remain outside this benchmark.

## FT inner shield bolts

The nine copper fasteners `nut1`--`nut9` are renamed `FTInnerShieldAndFlange_Bolt1`--`Bolt9`.
Threaded shafts and hexagonal head details are replaced by smooth solid 24-sided shafts and round heads.
Each mesh has 192 triangles: 16,278 combined triangles become 1,728 (89.38% fewer).
The original copper volumes are matched individually to within 0.0001%, including float32 STL rounding.
Materials, colors, mothers, and passive placements remain unchanged. The inner tip is shortened by
0.15 mm to separate it from the shield's blind-hole end face; a slightly adjusted shaft radius restores
its copper volume. The head stays inside the original across-flats envelope, at the original shoulder
and outer end. This deliberate material redistribution does not preserve the original threaded shape.

All nine outputs are closed, manifold, singly connected solids with no detected self-intersections or
zero-area faces. Triangle collision and enclosed-point checks in both directions find no intersection
with the unchanged optimized shield. Vertex-to-surface distances in both directions are at least
0.15 mm; these sampled distances are not a certified global clearance bound. Full default construction
and a separate shield-plus-bolts fixture provide Geant4 overlap checks.

`stls/bolts_mesh_health.json` retains the original hashes and model dimensions. The engineering originals
are archived in `clas12Tags/geometry_source/beamline/cad_original/`. Reproduce with the mesh-enabled Python:

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair bolts
/Users/ungaro/venv/pygemc/bin/python scripts/beamline_bolt_clearance.py --output /tmp/bolt-clearance.json
python3 scripts/beamline_cad_benchmark.py --pair bolts --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/bolts-benchmark --events 200 --repeats 5
```

The isolated nine-bolt benchmark uses matched 5 GeV primaries over 1.3--3.0 degrees and full azimuth.
The shield is excluded from transport timing and included separately in clearance checks. Loading,
transport, memory, and diagnostics are reported in the CAD optimization note with the earlier studies.

## FT outer flange

`outerFlange` is renamed `FTOuterFlange` in all ten applicable CAD variations. Its twelve bolt tunnels
are closed, while the central opening is retained. The flat annular surfaces are retriangulated using
all original inner and outer rim vertices at both z faces. The bounds, rim coordinates, stainless-steel
material, color, mother, and passive placement remain unchanged. The placement retains its original
1272.77 mm z offset, which differs from the inner-shield and mount offsets.

Triangles fall from 2,132 to 836 (60.79% fewer), and bytes fall from 106,684 to 41,884. The mesh remains
one closed manifold component, with genus reduced from 13 to 1. No self-intersections or zero-area faces
are detected. Closing the holes adds 32,343.387159 mm³ of stainless steel, increasing volume by 8.296635%.
Retriangulation preserves the hole-filled reference volume within floating-point precision. Bidirectional
surface sampling differs from that reference by at most 0.0000148 mm; this is a sampled maximum.

The original engineering STL is archived in `clas12Tags/geometry_source/beamline/cad_original/`.
`stls/outer_flange_mesh_health.json` records topology, hashes, material-volume changes, and shape checks.
Reproduce in the mesh-enabled environment, which provides pygemc's bolt-hole removal utility:

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair outer_flange
python3 scripts/beamline_cad_benchmark.py --pair outer_flange --executable /path/to/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/outer-flange-benchmark --events 200 --repeats 5
```

The isolated flange benchmark uses matched 5 GeV primaries over 1.9--2.8 degrees and full azimuth.
Loading, memory, particle tracking, and overlap diagnostics are retained in the CAD optimization note.
Timing changes include the added material and changed shower histories from filling the bolt tunnels.

For a comparison at fixed material volume, provide the hole-filled, unreduced flange with
`--filled-reference`. The reference has 2,084 triangles and the optimized flange has 836, with matching
volume, bounds, and rim geometry. The note retains a separate five-repetition control with 2,000 events
per particle and the same physics, acceptance, placements, and fixed executable:

```shell
python3 scripts/beamline_cad_benchmark.py --pair outer_flange \
  --filled-reference /tmp/filled.stl --executable /path/to/fixed/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/flange-filled-control --events 2000 --repeats 5
```

The control reference can be extracted from `hole_filled_reference/filled.stl` in the note's outer-flange
archive or regenerated with pygemc's `remove_holes.py` using the archived original and a 40 mm cutoff.
The control's `original` fixture label denotes this unreduced filled mesh, rather than the drilled original.

## FT outer mount

`outerMount` is renamed `FTOuterMount` in all ten applicable CAD variations. Four missing triangular faces
are repaired; the central passage and existing drilled openings are retained. The lower outer rim is
relieved by approximately 0.100 mm to clear `FTOuterFlange`, accounting for the original 0.5 mm difference
between their z placements. Adjacent sidewall facets interpolate toward unchanged upper vertices.
The mating facets are protected during simplification. Material, color, mother, and passive placement
are retained; the flange mesh is unchanged.

Triangles fall from 3,094 to 2,740 (11.44% fewer). The result is one closed manifold component with genus
11, no detected self-intersections, and no zero-area faces. Simplification differs from the relieved
reference by less than 0.05 mm under bidirectional vertex, edge, and surface sampling. The clearance relief
reduces volume by approximately 0.24924% against the sealed reference; the open engineering mesh has no
defined solid volume. `stls/outer_mount_mesh_health.json` records these references, hashes, and checks.

Placed-mesh triangle collision and containment checks find no mount/flange intersection. Clipping the
mount triangles to the flange's z range bounds the mount radius below the flange's minimum inner radius
by more than 0.035 mm. A separate 10,000-point Geant4 assembly check verifies the fit. The original mesh
is retained in `clas12Tags/geometry_source/beamline/cad_original/`.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair outer_mount
/Users/ungaro/venv/pygemc/bin/python scripts/beamline_mount_clearance.py --output /tmp/mount-clearance.json
python3 scripts/beamline_cad_benchmark.py --pair outer_mount --executable /path/to/fixed/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/outer-mount-benchmark --events 200 --repeats 5
```

The isolated tracking benchmark uses matched 5 GeV primaries over 1.5--2.4 degrees and full azimuth.
Results, raw diagnostics, material changes, and full assembly checks are retained in the CAD optimization
note. Repairs and relief change transport boundaries, so timings are not attributed only to triangle count.

## FT inner shield

Upcoming in the next release. `taggerInnerShield` is renamed `FTInnerShield` with its original
tungsten material and passive placement. Its defective 44,122-triangle surface is rebuilt from the
measured tube/flange profile and reduced to 6,500 triangles (85.27% fewer). The 60 mm central bore,
665 mm length, two longitudinal grooves with rounded ends, and tube/flange fillets are retained.
All 26 flange through-holes, all conical recesses, face chamfers and counterbores, and the tube hole
are filled. Both flange faces are smooth flat annuli. This supersedes the earlier 13,500-triangle
version that retained blind flange recesses; a further 7,000 triangles are removed (51.85%).

The final surface is closed, manifold, and genus one, with no detected self-intersections or zero-area
facets. All 512 flat flange facets and the groove/corner faces are protected during simplification.
An independent check confirms complete planar annuli and 1,134 inside/outside probes with no recess
walls. The new mesh adds 0.436019% tungsten volume relative to the prior closed mesh. Simplification
alone changes the smooth reference volume by -0.000846%; maximum sampled deviation is 0.047853 mm.
The open engineering original has no defined volume. `stls/ft_inner_shield_mesh_health.json` records
the smooth reference, geometry checks, and hashes. The CAD optimization note preserves the earlier
study and separately reports this smooth-flange revision and its tracking comparisons.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair ft_inner_shield --reference /tmp/ft-inner-shield-reference.stl
python3 scripts/beamline_cad_benchmark.py --pair ft_inner_shield \
  --filled-reference /tmp/ft-inner-shield-reference.stl --executable /path/to/fixed/gemc \
  --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/ft-inner-shield-smooth-control --events 200 --repeats 5
```

For the incremental upgrade comparison, supply the archived 13,500-triangle prior mesh with
`--filled-reference` and describe it using `--baseline-description`; use a fresh output directory.
Matched 5 GeV primaries cover 0.7--2.7 degrees and full azimuth. Filling the recesses changes material,
so upgrade timings are reported separately from the smooth-reference simplification control.

## Moller cone

The tenth beamline study renames main-cone to moller_cone in nine source and runtime GXML variations and
nine GEMC2 SQLite CAD rows. The beamline_W tungsten material, color, passive 180-degree y rotation, and
run-dependent positions remain unchanged. Five placements use cone z = 1589.27 mm and overlap the
FTInnerShield axial interval; four use z = 1273.27 mm and are already separated from the shield. The current
smooth-flange FTInnerShield is unchanged. The raw engineering cone is archived before replacement.

The original contains 15,782 triangles and 302 boundary edges in eight surface loops: five on the outer
tapered wall and three on the inner cylindrical wall. Its open surface has no valid enclosed material
volume. Filling those openings follows the measured outer cone and inner cylinder profiles, preserving every
original face and vertex before clearance work. The closed hole-filled reference has 16,688 triangles. The
large central beam passage remains open. A full nominal axisymmetric reconstruction is avoided because the
engineering outer rings are coarsely tessellated; their existing bounds and facets provide the shape
reference.

The existing entrance counterbore, about 39.98595 mm radius, is widened with a protected 128-sided
cylindrical cut of radius 40.200001 mm. The cut ends at local cone z = -53.53 mm, 0.2 mm beyond the
overlapping shield tip at -53.73 mm. A 0.2 mm nominal radial allowance above the shield radius accounts for
the polygonal opening. Independent clipped-triangle bounds give a minimum cone opening radius of 40.187892
mm and maximum shield radius 40.000001 mm, proving at least 0.187891 mm radial separation throughout the
shared axial interval. Collision checks and bidirectional vertex containment find no intersection in all
nine placements; the nearest sampled vertex-to-surface distance is 0.199938 mm in the overlapping group and
199.109193 mm in the axially separated group.

The clearance reference has 11,616 triangles; protected simplification retains 1,964 joint, shoulder, and
corner facets and produces 5,000 triangles, 68.32% fewer than the engineering input. File size falls from
789,184 to 250,084 bytes. The final mesh is one closed manifold component of genus one, with no detected
self-intersections or zero-area facets and exactly unchanged outer bounds. Minimum triangle altitude is
0.000380430 mm. Maximum sampled bidirectional displacement from the clearance reference is 0.020048 mm,
below the 0.05 mm shape guard. The original input reproduces the final STL and both reference meshes byte
for byte.

Hole-filled reference volume is 5835559.232219 mm3; final volume is 5825708.437762 mm3. Counterbore relief
and simplification remove 0.168806% tungsten relative to the closed hole-filled reference. Simplification
alone changes clearance-reference volume by -0.0000002660%. No original mass difference is inferred from the
defective open input. Fifty-five independent material probes test the filled opening centres and the
retained central beam passage.

Raw/final median transport ratios are 2.200, 1.739, 1.574, 1.552 for electrons, protons, positive pions, and
neutrons respectively. The raw cone emits 26 GeomSolids1001 and 396 GeomNav1002 exception blocks across the
recorded processes. Its stuck-track recovery and invalid solid prevent attributing these ratios solely to
tessellation reduction. The final mesh emits no Geant4 exceptions. The clean repaired-reference/final
comparison gives ratios 1.638, 1.313, 1.402, 1.301 in the same order, with no exceptions in either case.
Ratios above one mean faster tracking. These isolated timings do not establish full CLAS12 speedup or
physics-response equivalence. Median startup simulation time changes from 0.777853 to 0.744276 s; peak
startup RSS changes from 137.08 to 122.14 MiB.

A separate cone/shield assembly test uses 10,000-point Geant4 overlap checking. The original cone gives five
overlap reports and one solid warning; the final assembly has no warnings or overlaps. Full default beamline
construction completes with no missing meshes or solid warnings, retaining four overlap reports at the
unrelated downstream tube/adapter joints. The earlier shield studies retain their historical overlap
measurements; this cone revision resolves that interference. Semantic comparisons pass all fifteen native
geometry and material variations and fourteen CAD variations against GEMC2.


Rebuild the cone and retain both references for material and repaired-reference timing comparisons:

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair moller_cone --reference /tmp/moller-clearance-reference.stl \
  --repair-reference /tmp/moller-hole-filled-reference.stl
/Users/ungaro/venv/pygemc/bin/python scripts/beamline_cone_clearance.py \
  --output /tmp/moller-clearance.json
python3 scripts/beamline_cad_benchmark.py --pair moller_cone \
  --executable /path/to/fixed/gemc --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/moller-upgrade --events 200 --repeats 5
python3 scripts/beamline_cad_benchmark.py --pair moller_cone \
  --filled-reference /tmp/moller-clearance-reference.stl \
  --executable /path/to/fixed/gemc --database /tmp/beamline.sqlite \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/moller-reference-control --events 200 --repeats 5
```

The builder reads the owning GXML placements and the current smooth-flange FTInnerShield. The archive
retains that unchanged shield, all placement inputs, both references, final and reproduced meshes,
geometry database fixtures, raw logs/time reports/primaries, and archived scripts. The original cone is
open and emits solid and stuck-track warnings; only the repaired-reference control isolates decimation.
The binary itself is not redistributed; its SHA-256 is recorded in both benchmark metadata files.

## Moller cone tip

Upcoming in the next release. `cone-tip` is renamed `moller_cone_tip` in its four CAD configurations
(runs 5874, 11620, 18304, and 20000). Protected quadric decimation reduces 13,730 triangles to 5,000
(63.58% fewer), retaining one closed manifold genus-two component, both openings, exact bounds, and all
1,936 sharp-edge faces. No holes are filled. Maximum bidirectional sampled surface deviation is 0.0324 mm;
this is not a global error bound. Tungsten volume changes by -0.000486%, and materials and passive
placements are unchanged. The original is retained in `cad_original/`; the mesh-health report records hashes
and quality checks. The main-cone/tip overlap already exists with the original mesh and remains after this
optimization; complete affected configurations retain other source warnings.

The isolated five-seed benchmark uses 200 matched 5 GeV events per particle, 2.5--4.8 degrees, full azimuth,
FTFP_BERT, no field or optics, and one thread. Median tracking speedups are 1.659 for electrons, 1.133 for
protons, 1.177 for positive pions, and 1.159 for neutrons. All seed pairs are faster and isolated runs have no
Geant4 exceptions. These results do not establish full-experiment gains or detector-response equivalence.
The CAD optimization note retains raw results, full-assembly warnings, hashes, and reproduction inputs.


```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair cone_tip
python3 scripts/beamline_cad_benchmark.py --pair cone_tip --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/cone-tip-benchmark --events 200 --repeats 5
```

## FT flange

Upcoming in the next release. `flange-assembly` is renamed `FTFlange` in runs 5874, 11620, 18304, and
20000. Its already-coarse closed annulus is reduced from 552 to 540 triangles (2.17% fewer), with the
central passage, exact bounds, two flat face planes, stainless steel, and passive placement retained.
The result remains one closed manifold genus-one component with no detected self-intersections or
zero-area faces. No holes are filled. Maximum bidirectional sampled deviation is 0.049822 mm; this
is not a global bound. Steel volume changes by -0.000109%. The original is archived in `cad_original/`,
and the mesh-health report retains hashes and quality measurements.

Five repetitions of 2,000 matched 5 GeV events per particle over 1.4--3.8 degrees give median tracking
ratios of 1.0018, 1.0001, 1.0003, and 0.9993 for electrons, protons, positive pions, and neutrons.
All isolated runs complete without Geant4 exceptions. The paired ranges span one, so this study does
not establish a tracking-speed gain. Existing inner/outer assembly overlaps and an open inner assembly
remain. The CAD optimization note retains complete diagnostics, raw timings, and reproducible inputs.


```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair ft_flange
python3 scripts/beamline_cad_benchmark.py --pair ft_flange --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/ft-flange-benchmark --events 2000 --repeats 5
```

## Inner Moller-cone extension

Upcoming in the next release. `inner-assembly` is renamed `moller-cone-extension-inner` in runs
5874, 11620, 18304, and 20000. Its 75 open boundary edges are the two rims of a radial port with a
missing wall. Stitching the 35- and 40-vertex rims adds 75 faces without moving original vertices
or capping the beam passage or either port. The closed reference has 18,132 triangles and genus
three. Protected decimation retains 7,297 sharp-edge and port-adjacent faces and reduces it to 12,500
triangles, 30.77% fewer than the raw 18,057-triangle mesh. Bounds, stainless steel, and passive
placements remain unchanged. The saved mesh is closed and manifold with no detected intersections
or zero-area faces; its maximum sampled deviation from the repaired reference is 0.015669 mm.
This is a sampled measurement, not a global bound. Decimation changes the repaired steel volume
by +0.000009303%; the open original has no valid solid volume. Originals and mesh-health evidence
are retained. Separate raw-upgrade and repaired-reference tracking comparisons are recorded in the
CAD optimization note, along with existing assembly overlaps and remaining full-configuration warnings.
The clean-reference tracking speedups are 1.261, 1.086, 1.144, and 1.095 for electrons, protons,
positive pions, and neutrons in the isolated five-seed sample; every seed pair improves without warnings.


```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair extension_inner --reference /tmp/inner-extension-reference.stl
python3 scripts/beamline_cad_benchmark.py --pair extension_inner --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/inner-extension-upgrade --events 200 --repeats 5
python3 scripts/beamline_cad_benchmark.py --pair extension_inner --runno 5874 \
  --filled-reference /tmp/inner-extension-reference.stl --executable /path/to/fixed/gemc \
  --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/inner-extension-control --events 200 --repeats 5
```

## Moller-cone extension lead fill

Upcoming in the next release. This study renames `lead-shield` to `moller-cone-extension-lead-fill` in runs
5874, 11620, 18304, and 20000 in both repositories. The lead material, passive 180-degree y rotation, and
1273.27 mm z translation are retained. SQLite banks remain in `default`, selected by run number. The original
is archived, and all three installed optimized meshes are byte-identical.

The original is already a closed manifold solid with 10,594 triangles, one component, and genus two. Protected
quadric decimation reduces it to 8,000 triangles (24.4856% fewer), with 529,784 versus 400,084 stored bytes.
All 7,156 faces adjoining sharp edges above five degrees or any vertex within radius 48 mm retain their exact
triangle coordinates. This protects the full inner mating surface and adjacent end faces. The beam passage,
radial opening, and exact bounds remain. There is no hole filling or surface reconstruction. The result
retains its topology and has no boundary edges, non-manifold elements, detected intersections, or zero-area
triangles. Independent rebuilding reproduces its bytes.

Material volume changes from 11950334.138104 to 11950334.137844 mm³ (-0.0000000022%). Maximum bidirectional
vertex, edge, and surface sampled deviation is 0.00001998 mm, below the 0.05 mm guard. This sampled maximum is
not a proven global bound. Trials exceeding the shape, bounds, or volume guards are rejected.

The moller-cone extension lead fill retains its mating surface and openings with 24.49% fewer triangles.
Median isolated tracking ratios are 1.0826, 1.0795, 1.1226, 1.0882 for electrons, protons, positive pions, and
neutrons. Every paired measurement improves in this sample. Existing assembly overlaps remain.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair extension_lead
python3 scripts/beamline_cad_benchmark.py --pair extension_lead --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/extension_lead-benchmark --events 200 --repeats 5
```

## Moller-cone extension lead case

Upcoming in the next release. This study renames `outer-assembly` to `moller-cone-extension-lead-case` in runs
5874, 11620, 18304, and 20000 in both repositories. The stainless steel material, passive 180-degree y
rotation, and 1273.27 mm z translation are retained. SQLite banks remain in `default`, selected by run number.
The original is archived, and all three installed optimized meshes are byte-identical.

The original is already a closed manifold solid with 17,360 triangles, one component, and genus two. Protected
quadric decimation reduces it to 10,000 triangles (42.3963% fewer), with 868,084 versus 500,084 stored bytes.
All 9,105 faces adjoining sharp edges above five degrees or any vertex within radius 118 mm retain their exact
triangle coordinates. This protects the full inner mating surface and adjacent end faces. The beam passage,
radial opening, and exact bounds remain. There is no hole filling or surface reconstruction. The result
retains its topology and has no boundary edges, non-manifold elements, detected intersections, or zero-area
triangles. Independent rebuilding reproduces its bytes.

Material volume changes from 817759.770060 to 817759.420845 mm³ (-0.0000427038%). Maximum bidirectional
vertex, edge, and surface sampled deviation is 0.00678680 mm, below the 0.05 mm guard. This sampled maximum is
not a proven global bound. Trials exceeding the shape, bounds, or volume guards are rejected.

The moller-cone extension lead case retains its mating surface and openings with 42.40% fewer triangles.
Median isolated tracking ratios are 1.0529, 1.0377, 1.0098, 1.0198 for electrons, protons, positive pions, and
neutrons. Some paired ranges include one; those particle samples do not establish a consistent gain. Existing
assembly overlaps remain.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair extension_case
python3 scripts/beamline_cad_benchmark.py --pair extension_case --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/extension_case-benchmark --events 200 --repeats 5
```

## Moller-cone extension tungsten add-on

Upcoming in the next release. `outer-cone` is renamed `moller-cone-extension-tungsten-addon` in
runs 5874, 11620, 18304, and 20000. Bridging the 33- and 35-vertex rims restores a missing inclined
radial-port wall with 68 triangles while preserving all original vertex and triangle coordinates.
The beam passage and ports remain open. The repaired reference has 27,846 triangles and genus five.
Protected decimation retains 9,154 port, sharp-feature, and mating-interface faces and reduces the
mesh to 12,000 triangles, 56.80% fewer than the raw source. Bounds, tungsten material, and passive
placement are retained. Sampled deviation from the repaired reference is 0.012837 mm, and volume
changes by -0.0000046193%. The result is closed and manifold without detected intersections or
zero-area triangles. The main-cone mesh hash guards mating-face selection. The CAD optimization
note retains separate raw-input and repaired-reference tracking comparisons, geometry checks,
existing assembly overlaps, all raw timings, and reproducible inputs.


```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair extension_tungsten --reference /tmp/tungsten-reference.stl
python3 scripts/beamline_cad_benchmark.py --pair extension_tungsten --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/tungsten-upgrade --events 200 --repeats 5
python3 scripts/beamline_cad_benchmark.py --pair extension_tungsten --runno 5874 \
  --filled-reference /tmp/tungsten-reference.stl --executable /path/to/fixed/gemc \
  --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original \
  --output /tmp/tungsten-control --events 200 --repeats 5
```

## FT/cone joint clearances

Upcoming in the next release. This October 16 revision corrects the remaining FT/Moller-cone interfaces after
the individual mesh studies. Five meshes receive local material-removing operations: the inner extension, lead
fill, lead case, main cone, and tungsten add-on. FTInnerShield, FTFlange, and the cone tip remain
byte-identical. Placements, passive rotations, materials, names, and run keys are unchanged. All SQLite banks
remain in `default`, indexed by run number.

The inner-extension bore clears the placed FT shield, which is offset -369.73 mm in the common cone frame. Its
end is relieved around the unchanged flange bore. The lead-fill bore clears the inner extension. A scaled
convex envelope of the pre-clearance lead fill supplies at least 0.02002 mm plane clearance before final
casing simplification; a separate local cutter clears the unchanged flange. This envelope reduces casing
material loss from 4.4702% in a rejected circular-envelope trial to 1.2093%. The main cone receives a short
stepped relief around the inner-extension shoulder and a profiled opening around the cone tip. Its upper face
moves from z=712.002991 to 711.950012 mm. The add-on bore clears the main cone by a nominal 0.10 mm radial
profile margin. The health report retains every cutter profile and input hash.

Local FT/cone joint reliefs clear all eight checked interfaces while retaining the shield, flange, and cone
tip. Five meshes lose 0.119--1.209% material by volume. All affected complete configurations construct without
exceptions, and final corrected tracking runs are clean. Isolated tracking ratios 0.8568, 0.8541, 0.8465,
0.8920 describe the eight-part clearance revision; they are not pure decimation gains.

From the owning clas12-systems repository, run this pass last after reproducing individual mesh groups. Inputs
are archived in `cad_original/ft_joint_inputs_20261016/`; earlier shape and timing studies remain historical.
The current mesh-health reports retain their previous optimization records and reference the final joint
report.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py \
  --pair ft_joints --reference /tmp/ft-joint-case-reference.stl
python3 scripts/beamline_cad_benchmark.py --pair ft_joints --runno 5874 \
  --executable /path/to/fixed/gemc --database geometry_src/beamline/gemc.db \
  --originals ../clas12Tags/geometry_source/beamline/cad_original/ft_joint_inputs_20261016 \
  --output /tmp/ft-joints-benchmark --events 200 --repeats 5
```

## Generation and validation

Generate every native and CAD variation into SQLite:

```shell
build/subprojects/pygemc/python_env/bin/python3 geometry_src/beamline/beamline.py \
  -f sqlite -sql /tmp/beamline.sqlite
```

Generate and collect the runtime assets using the repository workflow:

```shell
./generate_geometry.zsh -s beamline --no-install
```

From the generated mesh directory, run the default beamline configuration:

```shell
cd experiments/beamline
gemc ../../geometry_src/beamline/beamline.yaml -sql=../gemc.sqlite
```

`beamline` holds native geometry; `beamline_cad` holds the run-specific CAD rows. Both use `factory: sqlite`.
Each CAD row points to `stls/<name>.stl` at scale 1, so the original mesh coordinates remain in millimetres.
Custom materials are published in both systems.

| Source configuration | Run | Beamline CAD |
|------------------|-----|--------------|
| default | 11 | yes |
| rga_spring2018 | 3029 | yes |
| rgk_winter2018 | 5874 | yes |
| rgb_spring2019 | 6150 | yes |
| rgf_spring2020 | 11620 | yes |
| rgc_summer2022 | 16000 | yes |
| rgd_fall2023 | 18304 | yes |
| rgl_spring2025 | 21000 | yes |
| rgc_fall2022 | 16843 | yes |
| rge_spring2024 | 20000 | yes |
| ddvcs | 10000201 | yes |
| rghFTOut | 10000202 | no source placements |
| rghFTOn | 10000203 | no source placements |
| TransverseUpstreamBeampipe | 10000204 | separate transverse CAD |
| elmo7 | 10000205 | no source placements |
| TransverseUpstreamBeampipe + forwardWedges | 10000206 | separate transverse CAD |
| TransverseUpstreamBeampipe + midpointWedges | 10000207 | separate transverse CAD |

Every SQLite geometry and material bank uses `variation=default`; the source labels above select the
authoring inputs and name the ASCII comparison files. Select another configuration by changing only `runno`:

```shell
gemc beamline.yaml -gui -runno=16000
```

This loads the ten native and twenty-two CAD volumes for `rgc_summer2022`. Regenerate an existing database
with the current builder before using this convention; the earlier generator stored named SQLite variations.
Omit `beamline_cad` for native configurations without source CAD placements. Custom runs use the beamline's
100-run allocation in `clas12_common.py`.

The separate `beamline_transverse_cad` system provides `noWedges` at run 10000204, `forwardWedges` at
10000206, and `midpointWedges` at 10000207, all under `default`. Its paths are `stls/<variant>/<name>.stl`.
The `beamline_transverse.yaml` card selects the upstream vacuum pipes and `noWedges`; override `runno` to
select either alternative. The corresponding native pipes and materials are present at all three runs. The
three models retain the same volume names and should be selected separately. The GEMC2 transverse example
lists all three models together; these are available here as alternatives rather than overlapping instances.

Validation:

```shell
build/subprojects/pygemc/python_env/bin/python3 scripts/compare_ascii_databases.py beamline
meson test -C build geometry_beamline gemc_beamline --print-errorlogs
```

The comparator checks all fifteen native geometry/material variations and all fourteen CAD placement
variations against the original TEXT/GXML references. The ten standard runs also match the named native and
CAD entries in `clas12Tags/clas12.sqlite`. That database has seven identical duplicate CAD rows at run 20000:
`beamline.pl` appends `cad_ddvcs.gxml` after the standard runs without changing the run. GEMC3 publishes those
seven names once, and separately makes the DDVCS CAD available at its custom run.

All fifteen native configurations and all three transverse CAD alternatives construct in GEMC with
`check_overlaps: 2`. The latest default construction has no missing meshes or solid warnings; no
overlap reports remain after the downstream socket correction. The optimized cone/shield assembly passes
the separate 10,000-point overlap check. Other configurations and raw meshes still require their own
validation; construction completing does not establish overlap-free geometry.

## Downstream socket clearance

Only Segment 1 is changed. Its entrance socket radius increases from 60.325 to 60.771702 mm through nominal
z = 5048.376367 mm, followed by a 1 mm transition back to the original bore. Two additional 24-vertex rings
replace one long wall band with three bands, adding 96 triangles. The downstream socket radius increases
from 70.6628 to 71.162277 mm over its existing downstream wall interval. Both sockets retain their angular
grids. The adapter, Segment 2, all outer bounds, materials, passive placements, and the open beam passage
remain unchanged.

The revised Segment 1 contains 5,096 triangles and 254,884 bytes, compared with 5,000 triangles and 250,084
bytes before relief. It remains one closed manifold genus-one component with no detected self-intersections
or zero-area triangles. Final volume is 6710837.897365 mm3, removing 0.604764% steel relative to the
previous closed mesh. Volume change against the original annularly repaired reference is -0.620987%. The
original engineering surface remains open and has no valid mass. Maximum sampled distance from that source
remains 0.745438 mm, within the existing 0.75 mm guard. The current builder reproduces the relieved STL byte
for byte.

Independent clipping of neighboring triangles to their shared axial intervals gives minimum clearance to all
48 socket-wall triangle planes of 0.100019 mm at the adapter and 0.100022 mm at Segment 2. Triangle
collisions and bidirectional vertex containment are zero for both pairs. All eleven source CAD
configurations containing the three volumes use the same identity placements, so the same joint checks apply
to each. The separate 10,000-point Geant4 assembly test gives eight overlap reports before relief and no
exceptions afterward. Full default beamline construction now finishes without missing meshes, solid
warnings, or overlap reports. These checks cover the tested configuration and do not certify every possible
complete detector assembly.

Previous/relieved median transport ratios are 0.981, 1.000, 1.008, 0.960 for electrons, protons, positive
pions, and neutrons respectively. Ratios above one denote faster tracking. The previous assembly produces 18
GeomNav1002, 4 GeomVol1002 exception blocks across the recorded processes; the relieved assembly produces 15
GeomNav1002 blocks. The remaining navigation warnings occur in the unchanged bellows region rather than
either relieved joint. Their z coordinates lie between 10177.906421 and 10281.864247 mm; all 1,741 triangles
intersecting the combined before/after warning interval are identical. Clean overlap checks therefore do not
establish warning-free tracking. These timings include overlap removal, local steel removal, and 96
additional facets. They measure the repair workload rather than a pure decimation gain, and do not establish
full CLAS12 performance or physics-response equivalence. The earlier study chapters and archives retain
their historical measurements.

```shell
/Users/ungaro/venv/pygemc/bin/python geometry_src/beamline/build_cad_meshes.py --pair downstream
/Users/ungaro/venv/pygemc/bin/python scripts/beamline_downstream_clearance.py \
  --output /tmp/downstream-clearance.json
python3 scripts/beamline_cad_benchmark.py --pair downstream_joints \
  --executable /path/to/fixed/gemc --database /tmp/beamline.sqlite \
  --originals /path/to/archive/previous --output /tmp/downstream-joint-benchmark --events 200 --repeats 5
```
