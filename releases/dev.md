## Development notes

- Added the first GEMC3 CLAS12 system port: `geometry_src/dc`.
- Added a template-style executable `dc.py` entry point that runs from the detector directory and writes GEMC
  geometry through `pygemc.autogeometry`.
- Added local DC run and variation mapping in `geometry_src/dc/variations.py`.
- Added a local coatjava bridge for DC geometry generation through `factory.groovy`.
- Preserved CLAS12Tags ordered rotations in the generated DB instead of flattening them to plain x/y/z
  rotations.
- Marked DC volumes with `g4placement_type = "passive"` so GEMC uses the GEMC2/clas12Tags Geant4 placement
  convention for ported CLAS12 detector geometry.
- Expanded the repository README with scope, layout, GEMC3/pygemc/home relationships, build/test workflow,
  coatjava notes, plugin conventions, and validation guidance.

## Commits on main since 2026-06-03

- 2026-06-05 **eaede76** — added reset flag to delete previous coatjava installations _(by Maurizio Ungaro)_
- 2026-06-04 **339f611** — added actual workflow _(by Maurizio Ungaro)_
- 2026-06-04 **4ebec14** — first implementation - expected to fail because git lfs is not working, needed by coatjava _(by Maurizio Ungaro)_
- 2026-06-03 **e77bd22** — Initial commit _(by Mauri)_
