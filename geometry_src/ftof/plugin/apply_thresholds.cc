// ftof plugin
#include "ftof.h"


bool FTOF_digitization::apply_thresholds_impl(GHit* ghit, GDigitizedData* digitizedData) {
    // Raw output keeps every hit. In normal output, GEMC2 applies this only when the
    // APPLY_THRESHOLDS-style option enrolls FTOF, so this hook is intentionally not intrinsic.
    if (ftc.outputRAW != 0 || !digitizedData->hasTransientVariable(FTOF_ATTENUATED_EDEP)) return false;

    // The framework only calls this for hits that digitizeHitImpl already accepted, so the
    // identity and per-paddle constants are valid here.
    const auto& gid = ghit->getGID();
    const int pmt  = gid[3].getValue();
    const int secI = gid[0].getValue() - 1;
    const int panI = gid[1].getValue() - 1;
    const int padI = gid[2].getValue() - 1;

    const double energyDepositedAttenuated = digitizedData->getTransientVariable(FTOF_ATTENUATED_EDEP);
    return energyDepositedAttenuated < ftc.threshold[secI][panI][pmt][padI];
}
