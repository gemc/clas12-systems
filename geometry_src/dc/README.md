# DC region-1 CAD

Upcoming in the next release: the six `dcs1r1back` through `dcs6r1back` membranes belong to DC,
in `cad/`, rather than magnets. Load the passive `dc` system, which includes the source meshes and copies.
Disabling DC digitization does not remove these passive volumes.
All CAD position coordinates are rounded to three decimal places in millimetres by the mesh builder.

Each original mesh has 12 vertices and 20 triangles. Proper rigid fits establish congruence within
0.00012 mm, comparable to single-precision STL coordinate rounding. One unchanged `dcs5r1back.stl`
therefore supplies all six original volume names through five `copyOf` placements. Stored and built
unique triangles fall from 120 to 20 (83.33%); the six physical membranes still contain 120 placed
triangles. Further decimation would remove corners from these already minimal hexagonal prisms.

The fits retain the original sector offsets. Integer angles are used after comparing the fitted and rounded
assemblies with 100,000 Geant4 surface samples per volume: no new overlap pairs and no overlaps involving
these membranes were found. This deliberate rounding displaces vertices by up to 0.76 mm; the fitted
placements match within 0.00012 mm. Materials, colors, and passive placement remain unchanged.
Sharing one thin membrane changes total signed Kapton volume by about 0.5%
because the original approximately 2.5-micrometre films have rounded STL coordinates.

SQLite publishes `dc` under `default` at runs 11, 3029, 4763, and the custom DC DDVCS run.
The survey run keys reuse the default native chambers; DDVCS retains its existing extra shields.
GEMC2 folds the ten back/support `CopyOf` rows into native `dc`; its two source meshes remain in `dc_cad`.
GEMC3 keeps all sources and copies in the main `dc` system because copy dependencies resolve within a system.
The main GEMC3 bank has 66 rows, or 72 for DDVCS. GEMC2 has 64 native rows, or 70 for DDVCS TEXT, plus two
CAD source rows. Cards no longer load a separate copy bank. Original meshes remain archived in GEMC2.

Consolidation leaves every mesh, opening, material, position, and rotation unchanged. Duplicate rows in the
old GEMC2 copy bank are removed; each named placement occurs once. This step removes no facets and establishes
no additional simulation speedup. The two shared meshes still contain 1,026 unique facets.

Reproduce the shared mesh, fitted placements, and metrics with the mesh-enabled pygemc environment:

```shell
/Users/ungaro/venv/pygemc/bin/python build_cad_meshes.py \
  --source ../../../clas12Tags/geometry_source/dc/cad_original --output /tmp/dc-back --round-angles
```

Use the local CCDB SQLite snapshot when generating or comparing native DC offline. The offline benchmark
in `scripts/dc_cad_benchmark.py` retains matched primaries and reports startup separately from tracking.

## Supports

Upcoming in the next release: `dcs1r1support` through `dcs6r1support` also belong to DC. Proper rigid fits
agree within 0.00012 mm. One unchanged `dcs1r1support.stl` supplies six named aluminum placements;
the existing two connected pieces and all openings are retained. Unique triangles fall from 6,036
to 1,006 (83.33% fewer); placed triangles remain 6,036. Sharing changes total signed aluminum volume
by less than 0.000002%. The active DC CAD system now has two STLs and twelve placements.

The original support surface has thirty faces flagged by MeshLab's intersection detector in its
contact region. These are retained. Trial decimation moved opening surfaces by submillimetre amounts
for little additional reduction, so the optimization shares the original solid without changing it.

Rebuild both groups from the archived originals with `--group all --round-angles`; the default
`--group back` retains the standalone membrane reproduction command above. The support benchmark uses
`--group support` and a 2--15 degree forward acceptance.
