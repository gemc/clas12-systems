// ecal plugin
#include "ecal.h"

// geant4
#include "Randomize.hh"

// c++
#include <cmath>


bool ECAL_digitization::apply_efficiency_impl(GHit* ghit, GDigitizedData* digitizedData) {
    // ECAL's clas12Tags "efficiency" is a DSC/TDC suppression, not a full-hit rejection.
    // Preserve that behavior by mutating only TDC_TDC to zero and returning false so the
    // ADC bank remains. The hook is intrinsic because clas12Tags applies it unconditionally.
    if (ecc.outputRAW != 0 || !digitizedData->hasTransientVariable(ECAL_UNROUNDED_ADC) ||
        !digitizedData->hasTransientVariable(ECAL_DTIME_IN_NS)) {
        return false;
    }

    const auto& gid = ghit->getGID();
    const int secI = gid[0].getValue() - 1;
    const int layerI = gid[1].getValue() - 1;
    const int stripI = gid[2].getValue() - 1;
    const double adc = digitizedData->getTransientVariable(ECAL_UNROUNDED_ADC);
    const double dtime_in_ns = digitizedData->getTransientVariable(ECAL_DTIME_IN_NS);
    const double def0 = ecc.deff[secI][layerI][0][stripI];
    const double def1 = ecc.deff[secI][layerI][1][stripI];
    const double def2 = ecc.deff[secI][layerI][2][stripI];

    if (def0 > 0 && dtime_in_ns > 0 &&
        G4UniformRand() > 1.0 / std::pow(1.0 + std::exp(-def0 * (adc / 10.0 - def1)), def2)) {
        digitizedData->includeVariable("TDC_TDC", 0);
    }
    return false;
}
