# DC region-1 CAD

Upcoming in the next release: the six `dcs1r1back` through `dcs6r1back` membranes belong to DC,
in `cad/`, rather than magnets. Load the passive `dc_cad` companion alongside native `dc`.
The experiment card also loads this companion when native DC digitization is disabled.
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

SQLite publishes the companion under `default` at runs 11, 3029, 4763, and the custom DC DDVCS run.
The six placements are identical across these banks. Native DC variations and geometry remain unchanged.
GEMC2 uses the same CAD source and a separate `dc_copies` native bank for its five `CopyOf` rows;
its supplied DC cards load both banks. Original six meshes are archived in the owning GEMC2 repository.

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
