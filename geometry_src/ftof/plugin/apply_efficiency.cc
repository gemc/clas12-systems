// ftof plugin
#include "ftof.h"

// geant4
#include "Randomize.hh"


bool FTOF_digitization::apply_efficiency_impl(GHit* ghit,
                                              [[maybe_unused]] GDigitizedData* digitizedData) {
    // FTOF inefficiency mirrors the GEMC2 DETECTOR_INEFFICIENCY policy. Keep the stochastic
    // draw in this dedicated hook so digitization remains deterministic and policy-free.
    if (ftc.outputRAW != 0) return false;

    const auto& gid = ghit->getGID();
    const int pmt  = gid[3].getValue();
    const int secI = gid[0].getValue() - 1;
    const int panI = gid[1].getValue() - 1;
    const int padI = gid[2].getValue() - 1;

    return G4UniformRand() > ftc.efficiency[secI][panI][pmt][padI];
}
