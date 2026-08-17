# CLAS12 GEMC Systems

[![Test][badge-test]][workflow-test]
[![ASCII Geometry Comparison][badge-ascii-geometry]][workflow-ascii-geometry]
[![Deploy][badge-deploy]][workflow-deploy]
[![Sanitize][badge-sanitize]][workflow-sanitize]
[![CodeQL Advanced][badge-codeql]][workflow-codeql]
[![Doxygen][badge-doxygen]][workflow-doxygen]
[![Binary Tarballs][badge-binary-tarballs]][workflow-binary-tarballs]
[![Nightly Dev Release][badge-dev-release]][workflow-dev-release]
[![HIPO Histos Comparison][badge-hipo-histos]][workflow-hipo-histos]
[![macOS Tarball][badge-macos-tarball]][workflow-macos-tarball]

[badge-test]: https://github.com/gemc/clas12-systems/actions/workflows/test.yml/badge.svg
[badge-ascii-geometry]: https://github.com/gemc/clas12-systems/workflows/ASCII%20Geometry%20Comparison/badge.svg
[badge-deploy]: https://github.com/gemc/clas12-systems/actions/workflows/deploy.yml/badge.svg
[badge-sanitize]: https://github.com/gemc/clas12-systems/actions/workflows/sanitize.yml/badge.svg
[badge-codeql]: https://github.com/gemc/clas12-systems/actions/workflows/codeql.yml/badge.svg
[badge-doxygen]: https://github.com/gemc/clas12-systems/actions/workflows/doxygen.yml/badge.svg
[badge-binary-tarballs]: https://github.com/gemc/clas12-systems/actions/workflows/binary_tarballs.yml/badge.svg
[badge-dev-release]: https://github.com/gemc/clas12-systems/actions/workflows/dev_release.yml/badge.svg
[badge-hipo-histos]: https://github.com/gemc/clas12-systems/actions/workflows/hipo_histos_compare.yml/badge.svg
[badge-macos-tarball]: https://github.com/gemc/clas12-systems/actions/workflows/macos_tarball.yml/badge.svg
[workflow-test]: https://github.com/gemc/clas12-systems/actions/workflows/test.yml
[workflow-ascii-geometry]: https://github.com/gemc/clas12-systems/actions/workflows/clas12_geo_compare.yml
[workflow-deploy]: https://github.com/gemc/clas12-systems/actions/workflows/deploy.yml
[workflow-sanitize]: https://github.com/gemc/clas12-systems/actions/workflows/sanitize.yml
[workflow-codeql]: https://github.com/gemc/clas12-systems/actions/workflows/codeql.yml
[workflow-doxygen]: https://github.com/gemc/clas12-systems/actions/workflows/doxygen.yml
[workflow-binary-tarballs]: https://github.com/gemc/clas12-systems/actions/workflows/binary_tarballs.yml
[workflow-dev-release]: https://github.com/gemc/clas12-systems/actions/workflows/dev_release.yml
[workflow-hipo-histos]: https://github.com/gemc/clas12-systems/actions/workflows/hipo_histos_compare.yml
[workflow-macos-tarball]: https://github.com/gemc/clas12-systems/actions/workflows/macos_tarball.yml

CLAS12 GEMC Systems contains the GEMC3 implementation of CLAS12 detector geometry systems and their
system-specific plugins. It is the CLAS12 companion repository to the core GEMC application and Python geometry
API:

- [`gemc/src`](https://github.com/gemc/src) provides the GEMC C++ application, Geant4 integration,
  SQLite/ASCII/CAD/GDML geometry loaders, dynamic plugin infrastructure, streamers, and bundled `pygemc`
  environment.
- [`gemc/pygemc`](https://github.com/gemc/pygemc) provides the Python API used to define geometry and materials,
  write GEMC databases, preview geometry with PyVista, and export VTK.js scenes.
- [`gemc/home`](https://github.com/gemc/home) contains the public GEMC website, installation pages, tutorials,
  examples, and generated documentation assets.

<br/>

## Current Scope

This repository is under active migration from [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags). The first GEMC3 system in the registry is:

| System  | Status              | Notes                                             |
|---------|---------------------|---------------------------------------------------|
| `dc`    | geometry and plugin | Uses coatjava as geometry source                  |
| `field` | plugin              | CLAS12 mapped magnetic field via the cMag library |


<br/>

## GEMC

The core GEMC repository, [`gemc/src`](https://github.com/gemc/src), owns the runtime behavior. This includes:

- Geant4 solid, logical-volume, and physical-placement construction
- dynamic C++ plugins 
- event generation, sensitive detectors, and output streamers

This repository owns CLAS12-specific inputs to that runtime:

- detector geometry, material definitions,
- run and variation mappings needed to reproduce CLAS12 geometry
- validation against GEMC2 CLAS12 reference geometry and output

The [`gemc/pygemc`](https://github.com/gemc/pygemc) repository defines the Python API.

<br/>

## Geometry Workflow

Each detector system is self-contained under `geometry_src/<system>`.

A typical system directory contains:

| File                                         | Role                                                                                 |
|----------------------------------------------|--------------------------------------------------------------------------------------|
| `<system>.py`                                | Executable main script; creates `autogeometry()` and publishes materials and volumes |
| `geometry.py`                                | Geometry construction code                                                           |
| `materials.py`                               | System material definitions                                                          |
| `variations.py`                              | Optional run and variation mapping                                                   |
| `<system>.yaml`                              | GEMC steering card for quick local runs                                              |
| `../coatjava_factories/CoatjavaFactory.java` | Optional coatjava bridge, in case of Java geometry services                          |
| `plugin/meson.build`                         | Optional C++ plugin registration for digitization or other runtime extensions        |

The main script should be executable and runnable directly from its directory:

```shell
cd geometry_src/dc
./dc.py 
```

Use PyVista options from `pygemc` when a system is ready for visual inspection:

```shell
./dc.py -pvb
```

Run GEMC with the local steering card:

```shell
gemc dc.yaml
gemc dc.yaml -gui
```

<br/>

## Reference Checks

Use `scripts/compare_ascii_databases.py` to compare generated GEMC3 ASCII databases (geometry and
materials) with the matching [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags) reference files:

```shell
scripts/compare_ascii_databases.py dc
```

With no system arguments, the script checks every local `geometry_src/<system>/<system>.py` implementation. The
script maps GEMC2 and GEMC3 ASCII columns onto common geometry fields — name, mother, position, rotation, solid,
dimensions, material, digitization (GEMC2 `sensitivity`), and identifier (GEMC2 `identifiers`, expanded to a
canonical `name=value` form) — and compares only those field values by volume name, so formatting and
column-order differences do not hide real geometry matches. Materials are compared the same way by material
name (density, components, optical and scintillation properties), for systems that define custom materials.

When any field differs the script prints the field-level mismatches and exits with status `1`; an all-match run
exits with status `0`.

<br/>

## Placement And Rotations

GEMC3 supports both Geant4 placement conventions through `GVolume.g4placement_type`:

| Value     | Meaning                                                                                |
|-----------|----------------------------------------------------------------------------------------|
| `active`  | Default GEMC3 behavior; uses `G4Transform3D(rotation, translation)`                    |
| `passive` | GEMC2/clas12Tags-compatible behavior; uses `G4PVPlacement(rotation, translation, ...)` |

CLAS12 detector volumes ported from GEMC2 should use the passive placement convention:

```python
gvolume.g4placement_type = "passive"
```

Keep ordered rotations ordered in the database. For example, do not flatten:

```text
ordered: yxz, 0*deg, 0*deg, 6*deg
```

GEMC applies ordered rotations in the specified order. This is required for DC and is expected to matter for
other CLAS12 systems ported from `clas12Tags`.

<br/>

## Coatjava

Some CLAS12 systems use coatjava so simulation geometry follows the same Java geometry service used by
reconstruction. This repository keeps coatjava local to `geometry_src`:

```shell
./geometry_src/install_coatjava.sh -l
```

Meson configure installs coatjava automatically if `geometry_src/coatjava` is missing. CI and Docker images must
provide the prerequisites first:

- Java
- Maven
- git-lfs
- jq

The helper scripts are:

| Path                               | Purpose                                                           |
|------------------------------------|-------------------------------------------------------------------|
| `geometry_src/install_coatjava.sh` | Installs the local coatjava copy                                  |
| `ci/install_coatjava_deps.sh`      | Installs Java, Maven, git-lfs, and jq in supported CI images      |
| `ci/setup_coatjava.sh`             | CI helper that installs prerequisites and then coatjava if needed |

Do not remove an existing coatjava installation unless the reset flag is explicitly requested.

<br/>

## Build And Test

This repository is built with Meson and uses the GEMC and Geant4 dependencies configured under `meson/`.

Configure, build, and test:

```shell
meson setup build --prefix="$PWD/install"
meson compile -C build
meson test -C build --print-errorlogs
```

The geometry tests run each registered Python system and write the combined SQLite database:

```shell
meson test -C build geometry_dc --print-errorlogs
sqlite3 build/clas12.db "select system, variation, run, count(*) from geometry group by 1,2,3;"
```

The CLAS12 system registry is currently in `meson.build`:

```meson
clas12_systems = [
    'dc',
]
```

Add a detector name to this list only when `geometry_src/<system>/<system>.py` is ready to generate valid GEMC
geometry.

<br/>

## CCDB Calibration Constants

The detector digitization plugins (`dc`, `ecal`, `ftof`, `ltcc`) load their calibration constants from CCDB. By
default they connect to the JLab database at `mysql://clas12reader@clasdb.jlab.org/clas12`; set the
`CCDB_CONNECTION` environment variable to point at a different server or a local SQLite snapshot
(`sqlite:///path/to/ccdb.sqlite`). Note this is the CCDB database, not the GEMC2 `clas12.sqlite` detector
database — pointing at the latter yields empty constants. On any CCDB failure (unreachable host, wrong database,
empty table) the plugins now abort the run with a clear error instead of silently producing empty digitized
output.

### MariaDB vs MySQL connector (macOS)

The CCDB client library needs care on macOS. The `clas12reader` account authenticates with
`mysql_native_password`, a scheme that Oracle **removed** from the MySQL client library in version 9.0 (it is
SHA1-based and was deprecated for security). A CCDB linked against MySQL 9.x therefore cannot authenticate to
clasdb and fails at connection time — this is a limitation of the client library, not a CCDB bug, and no CCDB
source change can restore a capability compiled out of the library. Install a connector that still provides it:

```shell
brew install mariadb-connector-c   # preferred: maintained; supports native_password and caching_sha2_password
# or
brew install mysql-client@8.4      # Oracle LTS that still ships native_password
```

The Meson build selects the CCDB connector automatically (`meson/meson.build`), preferring, in order,
`mariadb-connector-c`, `mysql-client@8.4`, `mysql-client`, then `mysql`, so a clean build links a working client
with no manual relink. If only MySQL 9.x is installed, CCDB still builds but connecting to clasdb fails with a
clear error until a compatible connector is installed (or the server account migrates to
`caching_sha2_password`).

There is a second, unrelated catch specific to MariaDB: `mariadb-connector-c` **enforces TLS by default**, while
clasdb runs without SSL, so an out-of-the-box MariaDB build fails with `Error 2026 (SSL is required, but the
server does not support it)`. The `ccdb` subproject is patched (via `subprojects/ccdb.wrap` `diff_files` →
`subprojects/packagefiles/ccdb_ssl_no_enforce.patch`) to disable TLS enforcement when built against MariaDB,
matching Oracle libmysqlclient's plaintext-fallback default. The patch is guarded with `#ifdef LIBMARIADB`, so it
is a no-op for the MySQL/Oracle clients (which removed that option and do not enforce TLS anyway). With that in
place, `mariadb-connector-c` connects to clasdb and is the recommended connector.

<br/>

## Plugin Path

CLAS12 system plugins are installed as `.gplugin` shared libraries under `<prefix>/lib/`. Because GEMC and
CLAS12 systems are installed to separate prefixes, GEMC needs to know where to look.

Set `GEMC_PLUGIN_PATH` to the CLAS12 systems library directory before running `gemc`:

```shell
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
gemc dc.yaml
```

Or pass it on the command line:

```shell
gemc dc.yaml -plugin_path=/path/to/clas12-systems/lib
```

When `GEMC_PLUGIN_PATH` is not set, GEMC falls back to its own `lib/` and `build/` directories and then
the OS dynamic-library search path (`LD_LIBRARY_PATH` on Linux, `DYLD_LIBRARY_PATH` on macOS).

If a plugin is not found, GEMC prints the current value of `GEMC_PLUGIN_PATH` alongside the error to help
diagnose path problems.

The installed prefix from a Meson build exposes the plugin directory through a pkg-config file:

```shell
# After: meson install -C build --prefix=/my/clas12/prefix
export PKG_CONFIG_PATH=/my/clas12/prefix/lib/pkgconfig:$PKG_CONFIG_PATH
export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
```

<br/>


## Plugin Build Model

System plugins use a registry pattern:

1. A detector-specific `geometry_src/<system>/plugin/meson.build` appends dictionaries to `clas12_plugins`.
2. The top-level `meson.build` is the only place that turns those entries into installed shared libraries.
3. Installed GEMC plugins must use the `.gplugin` suffix.

This keeps plugin installation consistent across CLAS12 systems and avoids each detector inventing its own build
logic.

<br/>

## Magnetic Field

CLAS12 uses a **mapped** magnetic field — the measured solenoid and torus field maps — rather than an analytic
model. The field is provided by the `gfieldclas12-cmag` plugin under `plugins/field/`, which reads the CLAS12
solenoid and torus binary maps through David Heddle's [cMag](https://github.com/JeffersonLab/clas12-cmag)
library (the `clas12-cmag` subproject) and returns the composite field at each step point.

The field is configured with the core GEMC generic `gfields` node, selecting this plugin with
`type: clas12-cmag`:

```yaml
gfields:
  - name: clas12
    type: clas12-cmag
    solenoid: Symm_solenoid_r601_phi1_z1201_13June2018
    torus: Symm_torus_r2501_phi16_z251_24Apr2018
    solenoid_scale: 1
    torus_scale: 1

global_field: clas12
```

The `global_field` value is the configured field name (`clas12` above), not the solenoid/torus map names. The
map names and the per-map scale factors belong to the `gfields` entry. This replaces the GEMC2
`global_field: Symm_solenoid_...:Symm_torus_...` style and the old hardcoded `binary_torus` /
`binary_solenoid` scale targets with explicit `torus`, `solenoid`, `torus_scale`, and `solenoid_scale`
parameters.

Any additional scalar keys (per-map displacements, overall origin/rotation, `interpolation`) are forwarded
verbatim to the plugin.

Field maps are downloaded to `<prefix>/fields` during `meson install` (see `meson/install_fields.py`) and the
plugin reads them from the `fields` directory installed next to it (`<plugin_dir>/../fields`). No `FIELD` or
`FIELD_DIR` environment variable is needed at runtime; an explicit `dir` parameter can override the location.

<br/>

## Validation

For each ported detector, validate both the produced database rows and the runtime geometry behavior.

Recommended checks:

- Compare generated geometry rows against the GEMC2 reference under `geometry_source/<system>` in
  [`gemc/clas12Tags`](https://github.com/gemc/clas12Tags).
- Confirm names, mothers, descriptions, positions, rotations, solids, parameters, and materials match where the
  fields are shared.
- Verify run and variation mappings are local to the system directory.
- Use PyVista exports for quick placement checks before running full Geant4.
- Run GEMC in batch and GUI modes when a detector has enough geometry to inspect.

For DC, the generated default geometry should token-match:

```text
https://github.com/gemc/clas12Tags/blob/main/geometry_source/dc/dc__geometry_default.txt
```

Known DC expectations:

- default run is `11`
- all DC volumes use `g4placement_type = "passive"`
- ordered rotations are preserved as `ordered: ...`
- obsolete `original` variation is not supported

<br/>

## CI And Releases

CI builds this repository against GEMC base images published by [`gemc/src`](https://github.com/gemc/src).
The [workflow guide](.github/workflows/README.md) documents triggers, deployment authorization,
cross-repository contracts, permissions, retries, and expected skipped runs.

Relevant automation:

| Workflow              | Purpose                                                                             |
|-----------------------|-------------------------------------------------------------------------------------|
| `deploy.yml`          | Build and test CLAS12 systems in GEMC base images, then publish the images          |
| `pr-docker-image.yml` | Build a per-PR preview image so reviewers can test the branch without a local build |
| `sanitize.yml`        | Run CLAS12-system sanitizer builds without sanitizing third-party subprojects       |
| `codeql.yml`          | Static analysis                                                                     |
| `doxygen.yml`         | Documentation generation                                                            |
| `binary_tarballs.yml` | Package installed CLAS12 systems prefixes                                           |
| `dev_release.yml`     | Development release automation                                                      |

Deploy images use the pattern:

```text
ghcr.io/gemc/clas12-systems:<gemc-tag>-<os>-<version>[-<arch>]
```

The base images come from:

```text
ghcr.io/gemc/src
```

Each pull request additionally publishes a ready-to-run, multi-arch preview image built from the branch
(`ghcr.io/gemc/clas12-systems:<gemc-tag>-almalinux-<version>-pr-<number>`), so authors and reviewers can test it
without a local build — see [Preview Container Image](CONTRIBUTING.md#preview-container-image) in the
contributing guide. The image is deleted automatically when the pull request is closed.

<br/>


## Documentation

- [CI workflow guide](.github/workflows/README.md)
- [GEMC homepage](https://gemc.github.io/home/)
- [Python API repository](https://github.com/gemc/pygemc)
- [GEMC2 / CLAS12 repository](https://github.com/gemc/clas12Tags)
