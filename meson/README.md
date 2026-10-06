# `meson/` — CLAS12 plugin build dependency setup

This directory holds `meson.build`, included from the top-level build with `subdir('meson')`. It resolves every
external dependency the CLAS12 detector plugins link against: the bundled subprojects (ccdb, hipo-cpp,
clas12-cmag), and the two dependencies shared with the GEMC core — CLHEP and Geant4. This README documents how
CLHEP and Geant4 are loaded, why there is no Qt6 here, and how this repository acts as the **consumer** of the
Geant4 pkg-config files that GEMC (`src`) produces.

The companion producer is `src/meson/README.md`: read both together, because the Geant4 handling only makes
sense as a producer/consumer pair.


## Producer / consumer model

This repository builds dlopen-able digitization/hit-process plugins (`.gplugin`) that load into an
already-built, already-installed GEMC. It does **not** discover Geant4 from `geant4-config`. Instead it consumes
the pkg-config files that GEMC installed into its own prefix:

- GEMC (`src`) generates and installs `geant4_core.pc` into `<gemc-prefix>/lib/pkgconfig` (Geant4 ships no
  pkg-config file of its own).
- This build resolves `geant4_core` from there, so the plugins are always built against the **exact** Geant4
  GEMC itself uses. A version mismatch is a hard error.

Because of this split, the Geant4 code here is deliberately smaller than in `src`: `src` runs `geant4-config`
and builds the full `-lG4*` link line once; this repo only needs the core set and only reads the resulting
`.pc`.


## Locating the installed GEMC

Two things are found from the installed GEMC, both with a graceful fallback so a plain "GEMC is installed and on
`PATH`" setup configures with no manual `PKG_CONFIG_PATH`:

- **`gemc` itself** via `dependency('gemc', ...)`; if pkg-config misses it, the prefix is derived from the
  `gemc` binary on `PATH` (`<dir of gemc>/..`) and `gemc.pc` is read from `<prefix>/lib/pkgconfig`.
- **`geant4_core.pc`** the same way: if `dependency('geant4_core')` misses, the GEMC prefix's `lib/pkgconfig` is
  prepended to `PKG_CONFIG_PATH` and pkg-config is run directly (`geant4_core.pc` has no `Requires`, so it is
  self-contained).

Only compile settings from `gemc` are propagated to the plugins (`partial_dependency(compile_args, includes)`);
GEMC exports its own symbols to loaded plugins, so its libraries are not linked into each plugin. GEMC's build
is also cross-checked: the Geant4 version in GEMC's installed `geant4_core.pc` must match the `geant4_core`
meson resolved, else configuration errors out.


## No Qt6

Qt6 is a GEMC-core (`src`) dependency for the GUI only. The CLAS12 plugins have no GUI, so there is no `qt6`
dependency in this build at all. Nothing to load, nothing to standardize.


## CLHEP

```meson
clhep_deps = dependency('clhep', version : '>=2.4.7.1', static : true, include_type : 'system')
```

Resolved through pkg-config exactly as in `src` — same module name `clhep`, same minimum version `2.4.7.1`,
same `include_type : 'system'`. The **one** intentional difference is `static : true`.

The plugins are `dlopen`-ed shared objects. Linking CLHEP (and Geant4, below) statically makes each `.gplugin`
embed only the symbols it references and carry **no** `@rpath/libCLHEP*` / `@rpath/libG4*` runtime dependency.
The shared variants resolve to install-name `@rpath/...`, but meson strips the build-tree rpath at install time
(no `install_rpath` is set on the plugin `shared_library`), which left an installed `.gplugin` with "no
LC_RPATH's found" and it failed to load. Static linking mirrors GEMC's own self-contained gstreamer plugins.

This is the opposite choice from `src`, and correctly so — see `src/meson/README.md` for why static CLHEP would
be wrong there:

- `src` needs GEMC and Geant4 to share a **single** copy of CLHEP's stateful globals (notably the `HepRandom`
  RNG singleton). Its executable resolves `libCLHEP` at run time via Geant4's rpath, so shared is both correct
  and necessary; static there would duplicate RNG state and trigger ODR errors in its shared/sanitizer builds.
- Here, each plugin is a single self-contained `dlopen` unit with a loader-path constraint, so static is the
  right call.

Same mechanism, opposite `static` flag, each justified by its own linking model.


## Geant4 (core only)

```meson
geant4_core_dep = dependency('geant4_core', version : '>=11.3.2', method : 'pkg-config',
                             static : true, include_type : 'system', required : false)
```

Only the **core** set is needed — plugins do not use the vis/GUI Geant4 libraries. Resolution:

1. Try plain pkg-config for `geant4_core` (`>=11.3.2`, static, system includes).
2. If not found, read `geant4_core.pc` from the installed GEMC's `lib/pkgconfig` (located as above). pkg-config
   is run directly with that dir prepended; the `-I` include flags are rewritten to `-isystem` to keep Geant4
   headers warning-free (what `include_type : 'system'` does for a pkg-config dependency).
3. If still not found, hard error telling the user to install GEMC (which provides `geant4_core.pc`) and put
   `gemc` on `PATH`.
4. Cross-check: the `geant4_core` version must match the one recorded in GEMC's installed `geant4_core.pc`, else
   error — the plugins must be built against the same Geant4 GEMC runs.

`static : true` here is for the same `.gplugin` loader reason as CLHEP.


## Bundled subprojects (brief)

- **ccdb** — built as the static `ccdb_static` archive (output `libccdb.a`) and embedded into the plugins,
  mirroring clas12Tags. The shared `libccdb` is never installed and its install-name points into the build
  prefix, so a `dlopen` of the plugin could not resolve it. Static is safe because `USE_SYSTEM_SQLITE` makes
  ccdb use the same system SQLite as GEMC (no duplicate `sqlite3` state). On macOS the MySQL/MariaDB connector
  is selected from Homebrew with a documented preference order (mariadb-connector-c first) so ccdb can still
  authenticate to clasdb.jlab.org's `mysql_native_password` reader account.
- **hipo-cpp**, **clas12-cmag** — built as static subprojects, or taken from an explicit external installation
  via `-Duse-hipo-location` / `-Duse-clas12-cmag-location` (and `-Duse-ccdb-location`), which bypass the
  subproject and its discovery entirely.
- Subproject libraries/headers/tools/tests are not installed or registered unless the caller opts in with
  `-Dinclude-subproject-install` / `-Dinclude-subproject-tests`; the installed GEMC already ships these.
