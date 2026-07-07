// dc plugin
#include "dc.h"

// geant4
#include "Randomize.hh"


bool DC_digitization::apply_efficiency_impl([[maybe_unused]] GHit* ghit, GDigitizedData* digitizedData) {
    // clas12Tags applies this DC inefficiency unconditionally in dc_HitProcess::integrateDgt:
    // reject the hit if the distance-dependent random draw fails, or if the fractional DOCA
    // falls outside the half-cell. GEMC3 marks this as an intrinsic efficiency policy, so the
    // framework calls this hook even when the global -applyInefficiencies option is absent.
    if (!digitizedData->hasTransientVariable(DC_FRACTIONAL_DOCA) ||
        !digitizedData->hasTransientVariable(DC_INEFFICIENCY)) {
        return false;
    }

    const double x = digitizedData->getTransientVariable(DC_FRACTIONAL_DOCA);
    const double inefficiency = digitizedData->getTransientVariable(DC_INEFFICIENCY);
    return G4UniformRand() < inefficiency || x > 1.0;
}
