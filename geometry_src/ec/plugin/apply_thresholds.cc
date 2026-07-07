// ecal plugin
#include "ecal.h"


bool ECAL_digitization::apply_thresholds_impl(GHit* ghit, GDigitizedData* digitizedData) {
    // clas12Tags applies the ECAL FADC threshold inside ecal_hitprocess::integrateDgt.
    // GEMC3 keeps the rejection in this dedicated hook. ECAL declares thresholds intrinsic
    // because this policy is part of the detector response, not an optional global overlay.
    if (ecc.outputRAW != 0 || !digitizedData->hasTransientVariable(ECAL_UNROUNDED_ADC)) return false;

    const auto& gid = ghit->getGID();
    const int secI = gid[0].getValue() - 1;
    const int layerI = gid[1].getValue() - 1;
    const int stripI = gid[2].getValue() - 1;
    const double adc = digitizedData->getTransientVariable(ECAL_UNROUNDED_ADC);

    // GEMC2 compares the unrounded FADC amplitude scaled by 1/10 against fthr.
    return adc / 10.0 < ecc.fthr[secI][layerI][stripI];
}
