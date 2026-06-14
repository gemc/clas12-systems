# Porting clas12Tags Hit Processes to GEMC3

This document records the patterns and gotchas discovered while porting the DC hit process.
Use it as the primary reference when porting additional systems.

Reference implementation: `geometry_src/dc/plugin/`
Source of truth: `../clas12Tags/source/hitprocess/clas12/<system>_hitprocess.{h,cc}`

---

## Plugin file layout

Each system plugin lives under `geometry_src/<system>/plugin/` and contains:

| File | GEMC2 equivalent | Purpose |
|---|---|---|
| `<system>.h` | class declaration | Plugin class, inherits `GDynamicDigitization` |
| `readoutSpecs.cc` | — | `defineReadoutSpecsImpl` + factory entry points |
| `process_gtouchable.cc` | `processID` | Map raw step → (layer, wire/strip/…) identity |
| `calibration_constants.cc` | `initializeDCConstants` | Load CCDB calibration tables into a constants struct |
| `load_tt.cc` | `initializeDCConstants` (TT block) | Load `/daq/tt/<system>` translation table from CCDB |
| `digitize_hit.cc` | `integrateDgt` | Compute the digitized observable (TDC, ADC, …) |
| `meson.build` | — | Register plugin in the `clas12_plugins` list |

---

## meson.build

Append one dictionary to `clas12_plugins`.  Always list all `.cc` files and declare
`ccdb_dep` when the plugin reads from CCDB.

```meson
clas12_plugins += [{
    'name'                : '<system>',
    'sources'             : files('readoutSpecs.cc', 'process_gtouchable.cc',
                                   'calibration_constants.cc', 'load_tt.cc', 'digitize_hit.cc'),
    'dependencies'        : [gemc_dep, ccdb_dep],
    'include_directories' : [include_directories('.')],
}]
```

The top-level `meson.build` turns these entries into installed `.gplugin` shared libraries;
never add `shared_library()` calls inside the plugin directory.

---

## Class header (`<system>.h`)

```cpp
#pragma once
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"
#include "<system>_constants.h"

class SYS_digitization : public GDynamicDigitization {
public:
    explicit SYS_digitization(const std::shared_ptr<GOptions>& g)
        : GDynamicDigitization(g) {
        log = std::make_shared<GLogger>(g, "SYS_digitization", "<system>");
    }

    bool defineReadoutSpecsImpl() override;

    std::vector<std::shared_ptr<GTouchable>> processTouchableImpl(
        std::shared_ptr<GTouchable>, G4Step*) override;

    bool loadConstantsImpl(int runno, std::string const& variation) override;
    bool loadTTImpl(int runno, std::string const& variation) override;

    [[nodiscard]] std::unique_ptr<GDigitizedData>
        digitizeHitImpl(GHit* ghit, size_t hitn) override;

    SYSConstants scc;   // calibration/geometry constants struct
};
```

The `"<system>"` string in `GLogger` becomes the verbosity key:
`-verbosity.<system>=2` or `verbosity.<system>: 2` in YAML.

---

## readoutSpecs.cc — `defineReadoutSpecsImpl` + factory symbols

`defineReadoutSpecsImpl` constructs `readoutSpecs` from the time window, grid start time,
and max step size.  The time-window value should be exposed via `definePluginOptions` so
users can override it on the command line or in YAML.

**Required factory symbols** (do not rename):

```cpp
extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new SYS_digitization(g));
}

extern "C" GOptions* definePluginOptions() {
    auto* opts = new GOptions("<system>");
    opts->defineOption(
        GVariable("<system>_timeWindow", <default_ns>, "<system> time window [ns]"), "...");
    return opts;
}
```

---

## process_gtouchable.cc — porting `processID`

`processTouchableImpl` receives a `GTouchable` and the live `G4Step*`, updates the
touchable identity indices, and delegates to the base class.

Key API differences from GEMC2:

- **Get detector dimensions**: `gtouchable->getDetectorDimensions()` returns a
  `std::vector<double>` of the G4 solid parameters in G4 internal units (mm).  For
  `G4Trap` the order is `[dz, theta, phi, dy1, dx1, dx2, alpha1, dy2, dx3, dx4, alpha2]`.
- **Transform global → local**: use the pre-step touchable history transform:
  ```cpp
  G4ThreeVector Lxyz =
      thisStep->GetPreStepPoint()->GetTouchableHandle()
               ->GetHistory()->GetTopTransform().TransformPoint(xyz);
  ```
- **Update identity**: `gtouchable->setIdentityValue(index, value)` (0-based index).
  Identity order matches the `identifiers` list in the geometry Python script.
- **Always delegate**: return `GDynamicDigitization::processTouchableImpl(std::move(gtouchable), thisStep)`
  at the end so the base class handles time-cell binning.

---

## calibration_constants.cc — porting `initializeDCConstants`

Standard CCDB access pattern:

```cpp
const char* env  = std::getenv("CCDB_CONNECTION");
std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
char db[256];

std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
std::vector<std::vector<double>> data;

snprintf(db, sizeof(db), "/calibration/<system>/table:%d:%s", runno, variation.c_str());
calib->GetCalib(data, db);
```

For tables accessed via the assignment API (e.g. geometry tables):

```cpp
snprintf(db, sizeof(db), "/geometry/<system>/table:%d:%s", runno, variation.c_str());
std::unique_ptr<ccdb::Assignment> asgn(calib->GetAssignment(db));
for (size_t row = 0; row < asgn->GetRowsCount(); row++) {
    value = asgn->GetValueDouble(row, col);
}
```

CCDB row indices are **1-based** in the raw table (column 0 = sector, column 1 = superlayer, …);
always subtract 1 when storing into 0-based C++ arrays.

---

## load_tt.cc — porting the translation-table block

The translation table maps hardware addresses `(crate, slot, channel)` to detector
identities `{sector, layer, component, …}`.

```cpp
bool SYS_digitization::loadTTImpl(int runno, std::string const& variation) {
    // … CCDB setup …
    snprintf(db, sizeof(db), "/daq/tt/<system>:%d:%s", runno, variation.c_str());
    calib->GetCalib(data, db);

    auto tt = std::make_shared<GTranslationTable>(gopts);
    for (const auto& row : data) {
        int crate  = static_cast<int>(row[0]);
        int slot   = static_cast<int>(row[1]);
        int chan   = static_cast<int>(row[2]);
        // remaining columns: detector identity (system-specific order)
        tt->addGElectronicWithIdentity({id1, id2, …}, GElectronic(crate, slot, chan, 2));
    }
    translationTable = tt;   // base-class shared_ptr<const GTranslationTable>
    return true;
}
```

`mode=2` means full crate/slot/channel resolution.  The identity vector must match the
order used by `processTouchableImpl` exactly.

To discover the column order for a new system when no C++ loader exists in clas12Tags,
look at `coatjava_src/…/TranslationTable.java` for the system.

---

## digitize_hit.cc — porting `integrateDgt`

### GHit API (GEMC3)

| GEMC2 accessor | GEMC3 equivalent | Notes |
|---|---|---|
| `identity[i]` | `ghit->getGID()[i].getValue()` | 1-based, same order as identifiers list |
| `Lpos[i]` | `ghit->getLocalPositions()[i]` | `G4ThreeVector`, G4 internal units (mm) |
| `Edep[i]` | `ghit->getEdeps()[i]` | G4 internal units (MeV) |
| `time[i]` | `ghit->getTimes()[i]` | G4 internal units (ns) |
| `mom[i]` | `ghit->getMomenta()[i]` | `G4ThreeVector`, G4 internal units (MeV) |
| `trackE[i]` | `ghit->getTrackEs()[i]` | total energy (MeV) |
| `trackId[i]` | `ghit->getTids()[i]` | int track ID |
| number of steps | `ghit->nsteps()` | size_t |
| detector dimensions | `ghit->getDetectorDimensions()` | `vector<double>`, mm |

### Unit conversion

GEMC3 stores everything in G4 internal units.  When the GEMC2 code uses a value in
physical units, convert explicitly with CLHEP:

```cpp
#include <CLHEP/Units/SystemOfUnits.h>
using namespace CLHEP;

double doca_cm  = DOCA.mag() / cm;     // G4 mm → cm
double time_ns  = times[s]   / ns;     // G4 ns → ns (identity, but explicit)
double vel_cmns = v0_cm_per_ns * cm / ns;  // cm/ns → G4 internal
double edep_eV  = edeps[s]   / eV;     // G4 MeV → eV for threshold comparison
```

### B-field

GEMC3 `GHit` does **not** store the magnetic field at the step.  Set `thisMgnf = 0.0`;
all B-field-dependent correction terms will vanish automatically (they are proportional
to `bfield²`).

### Two-loop pattern

Loop 1 — fastest signal arrival (determines the primary trackId):
```cpp
// signal = stepTime + DOCA/v0   (arrival time at the wire)
// choose step with minimum signal; require edep > threshold for trackIds
```

Loop 2 — smallest DOCA on the primary track (determines alpha and beta):
```cpp
// alpha = local track angle at the wire; used in calc_Time
// beta  = p/E of the particle; used in calc_TimeBeta and doca_smearing
```

### Faithfully reproducing GEMC2 bugs / intentional quirks

Some GEMC2 behaviours must be preserved for numerical agreement with reconstruction:

- **`prop_t` excluded from `signal_t`**: propagation time is NOT used when searching for
  the fastest step.  It is added to `smeared_time` at the end.  The GEMC2 source marks
  this with a `// FIXME` comment; replicate as-is.
- **`sl_sign` loop bug**: the GEMC2 loop over `i=0..2` with `if(SLI==2*i+1) sl_sign=-1;
  else sl_sign=1;` overwrites on every iteration, so only `SLI==5` yields `-1`.
  Replicate as `const int sl_sign = (SLI == 5) ? -1 : 1`.
- **`fieldPolarity`**: not stored in GEMC3; the B-field correction term is zero anyway
  when `thisMgnf=0`.

### GDigitizedData output

```cpp
auto dgt = std::make_unique<GDigitizedData>(gopts, ghit);
dgt->includeVariable("hitn",      static_cast<int>(hitn));
dgt->includeVariable("sector",    sector);
dgt->includeVariable("layer",     layer_or_global_layer);
dgt->includeVariable("component", wire_or_strip);
dgt->includeVariable("TDC_order", 0);
dgt->includeVariable("TDC_TDC",   smeared_time_ns);
// ADC variables as needed: "ADC_order", "ADC_ADC", "ADC_time", "ADC_ped"
return dgt;
```

Return `nullptr` to drop the hit (inefficiency rejection, out-of-bounds wire, …).

---

## G4Trap dimension index reference

`getDetectorDimensions()` for a `G4Trap` returns 11 values (all in mm):

| Index | Symbol | Meaning |
|---|---|---|
| 0 | `dz` | half-thickness along z |
| 1 | `theta` | polar angle of the line joining centres of faces |
| 2 | `phi` | azimuthal angle |
| 3 | `dy1` | semi-height at −z face |
| 4 | `dx1` | half-width at (−z, −y) |
| 5 | `dx2` | half-width at (−z, +y) |
| 6 | `alpha1` | tilt angle at −z face |
| 7 | `dy2` | semi-height at +z face |
| 8 | `dx3` | half-width at (+z, −y) |
| 9 | `dx4` | half-width at (+z, +y) |
| 10 | `alpha2` | tilt angle at +z face |

For a symmetric `G4Trap` (as used by DC superlayers) `dy1 == dy2` and `dx1 == dx3`,
`dx2 == dx4`, so index 3 (dy1) is the wire-number axis half-height and index 0 (dz) is
the wire-depth axis half-thickness.

---

## Checklist for a new system port

1. [ ] Create `geometry_src/<system>/plugin/` directory.
2. [ ] Write `<system>_constants.h` mirroring the GEMC2 constants struct.
3. [ ] Write `<system>.h` declaring all five `…Impl` overrides.
4. [ ] Write `readoutSpecs.cc` with `defineReadoutSpecsImpl` and the two factory symbols.
5. [ ] Port `processID` → `process_gtouchable.cc`.
6. [ ] Port `initializeDCConstants` (calibration part) → `calibration_constants.cc`.
7. [ ] Port `initializeDCConstants` (TT block) → `load_tt.cc`; verify column order against
       Java coatjava if no C++ TT loader exists.
8. [ ] Port `integrateDgt` → `digitize_hit.cc`; apply unit conversions and preserve GEMC2
       quirks listed above.
9. [ ] Add the plugin entry to `geometry_src/<system>/plugin/meson.build`.
10. [ ] Run `meson test -C build --suite clas12` and verify the geometry test passes before
        touching the plugin code.
11. [ ] After integrating the plugin, confirm that `ci/build.sh` exits with `Failures: 0`.
