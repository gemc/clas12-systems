#include "ltcc.h"

// geant4
#include "G4OpticalPhoton.hh"
#include "Randomize.hh"

// CLHEP
#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <map>


std::unique_ptr<GDigitizedData> LTCC_digitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& gid = ghit->getGID();
    if (gid.size() < 3 || ghit->nsteps() == 0) return nullptr;

    const int sector = gid[0].getValue();
    const int side = gid[1].getValue();
    const int segment = gid[2].getValue();

    if (!valid_index(sector, side, segment)) return nullptr;

    const int secI = sector - 1;
    const int sideI = side - 1;
    const int segI = segment - 1;
    const double tdcConv = ltccc.tdcConv[secI][sideI][segI];
    if (tdcConv == 0) return nullptr;

    auto digitizedData = std::make_unique<GDigitizedData>(gopts, ghit);

    if (ghit->getPid() != G4OpticalPhoton::OpticalPhotonDefinition()->GetPDGEncoding()) {
        digitizedData->includeVariable("sector", -sector);
        digitizedData->includeVariable("layer", -side);
        digitizedData->includeVariable("component", -segment);
        return digitizedData;
    }

    std::map<int, double> photonEnergy;
    const auto tids = ghit->getTids();
    const auto trackE = ghit->getTrackEs();
    for (size_t s = 0; s < tids.size() && s < trackE.size(); s++) {
        if (photonEnergy.find(tids[s]) == photonEnergy.end()) {
            photonEnergy[tids[s]] = trackE[s];
        }
    }

    int ndetected = 0;
    for (const auto& [tid, energy] : photonEnergy) {
        double probability = 1.0;
        auto probIt = photonDetectionProbability.find(photon_key(gid, tid));
        if (probIt != photonDetectionProbability.end()) {
            probability = probIt->second;
            photonDetectionProbability.erase(probIt);
        }

        if (G4UniformRand() <= probability) ndetected++;
    }

    const double adc = CLHEP::RandGauss::shoot(ndetected * ltccc.speMean[secI][sideI][segI],
                                               ndetected * ltccc.speSigma[secI][sideI][segI]);
    const double timeOffset = CLHEP::RandGauss::shoot(ltccc.timeOffset[secI][sideI][segI],
                                                      ltccc.timeRes[secI][sideI][segI]);
    const double timeInNs = ghit->getAverageTime() / ns + timeOffset;
    const double fadcTime = convert_to_precision(timeInNs);
    const int tdc = static_cast<int>(timeInNs / tdcConv);

    digitizedData->includeVariable("hitn", static_cast<int>(hitn));
    digitizedData->includeVariable("sector", sector);
    digitizedData->includeVariable("layer", side);
    digitizedData->includeVariable("component", segment);
    digitizedData->includeVariable("ADC_order", 0);
    digitizedData->includeVariable("ADC_ADC", adc);
    digitizedData->includeVariable("ADC_time", fadcTime);
    digitizedData->includeVariable("ADC_ped", 0);
    digitizedData->includeVariable("TDC_order", 0);
    digitizedData->includeVariable("TDC_TDC", tdc);

    return digitizedData;
}
