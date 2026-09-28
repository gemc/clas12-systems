#include "htcc.h"

// geant4
#include "G4OpticalPhoton.hh"
#include "Randomize.hh"

// CLHEP
#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <map>


std::unique_ptr<GDigitizedData> HTCC_digitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& gid = ghit->getGID();
    if (gid.size() < 3 || ghit->nsteps() == 0) return nullptr;

    // Geometry identity order: sector, ring, half. The bank stores half as "layer" and ring as
    // "component" (clas12Tags htcc bank.pl / htcc_hitprocess integrateDgt).
    const int sector = gid[0].getValue();
    const int ring = gid[1].getValue();
    const int half = gid[2].getValue();

    if (!valid_index(sector, ring, half)) return nullptr;

    const int secI = sector - 1;
    const int halfI = half - 1;
    const int ringI = ring - 1;
    const double tdcConv = htccc.tdcConv[secI][halfI][ringI];
    if (tdcConv == 0) return nullptr;

    // clas12Tags htcc_hitprocess returns an empty record for non-optical-photon hits (only Cherenkov
    // photons detected on the PMT photocathode produce a signal).
    if (ghit->getPid() != G4OpticalPhoton::OpticalPhotonDefinition()->GetPDGEncoding()) {
        return nullptr;
    }

    // Collect the initial energy of each unique optical-photon track contributing to this hit.
    std::map<int, double> photonEnergy;
    const auto tids = ghit->getTids();
    const auto trackE = ghit->getTrackEs();
    for (size_t s = 0; s < tids.size() && s < trackE.size(); s++) {
        if (photonEnergy.find(tids[s]) == photonEnergy.end()) {
            photonEnergy[tids[s]] = trackE[s];
        }
    }

    // Accept each unique photon with its cached photocathode quantum efficiency.
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

    // ADC = gain * Gauss(ndetected * mc_gain, ndetected * mc_smear); time = hit time + veff shift +
    // per-ring shift (clas12Tags htcc_hitprocess integrateDgt).
    const double adc = htccc.gain[secI][halfI][ringI] *
                       CLHEP::RandGauss::shoot(ndetected * htccc.mcGain[secI][halfI][ringI],
                                               ndetected * htccc.mcSmear[secI][halfI][ringI]);
    const double timeInNs = ghit->getAverageTime() / ns +
                            htccc.timeShift[secI][halfI][ringI] + htccc.ringShift[ringI];
    const double fadcTime = convert_to_precision(timeInNs);
    const int tdc = static_cast<int>(timeInNs / tdcConv);

    auto digitizedData = std::make_unique<GDigitizedData>(gopts, ghit);
    digitizedData->includeVariable("hitn", static_cast<int>(hitn));
    digitizedData->includeVariable("sector", sector);
    digitizedData->includeVariable("layer", half);
    digitizedData->includeVariable("component", ring);
    digitizedData->includeVariable("ADC_order", 0);
    digitizedData->includeVariable("ADC_ADC", static_cast<int>(adc));
    digitizedData->includeVariable("ADC_time", fadcTime);
    digitizedData->includeVariable("ADC_ped", 0);
    digitizedData->includeVariable("TDC_order", 0);
    digitizedData->includeVariable("TDC_TDC", tdc);

    return digitizedData;
}
