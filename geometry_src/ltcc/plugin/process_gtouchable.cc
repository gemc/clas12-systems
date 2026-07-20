#include "ltcc.h"

// geant4
#include "G4Material.hh"
#include "G4MaterialPropertiesTable.hh"
#include "G4MaterialPropertyVector.hh"
#include "G4OpticalPhoton.hh"


bool LTCC_digitization::valid_index(int sector, int side, int segment) {
    return sector >= 1 && sector <= LTCCConstants::NSECT &&
           side >= 1 && side <= LTCCConstants::NSIDE &&
           segment >= 1 && segment <= LTCCConstants::NSEGM;
}


LTCC_digitization::PhotonKey LTCC_digitization::photon_key(const std::vector<GIdentifier>& gid, int trackId) {
    return {gid[0].getValue(), gid[1].getValue(), gid[2].getValue(), trackId};
}


bool LTCC_digitization::decisionToSkipHit(double energy, const G4Step* thisStep) {
    if (thisStep == nullptr || thisStep->GetTrack() == nullptr) return true;

    if (thisStep->GetTrack()->GetDefinition() == G4OpticalPhoton::OpticalPhotonDefinition()) {
        return false;
    }
    return GDynamicDigitization::decisionToSkipHit(energy);
}


std::vector<std::shared_ptr<GTouchable>> LTCC_digitization::processTouchableImpl(
    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) {

    if (thisStep != nullptr && thisStep->GetTrack() != nullptr &&
        thisStep->GetTrack()->GetDefinition() == G4OpticalPhoton::OpticalPhotonDefinition()) {

        double probability = 1.0;
        auto* volume = thisStep->GetPreStepPoint()->GetTouchableHandle()->GetVolume();
        if (volume != nullptr && volume->GetLogicalVolume() != nullptr) {
            auto* material = volume->GetLogicalVolume()->GetMaterial();
            auto* mpt = material == nullptr ? nullptr : material->GetMaterialPropertiesTable();
            auto* efficiency = mpt == nullptr ? nullptr : mpt->GetProperty("EFFICIENCY");
            if (efficiency != nullptr) {
                bool outOfRange = false;
                probability = efficiency->GetValue(thisStep->GetTrack()->GetTotalEnergy(), outOfRange);
            }
        }

        auto gid = gtouchable->getIdentity();
        if (gid.size() >= 3) {
            photonDetectionProbability[photon_key(gid, thisStep->GetTrack()->GetTrackID())] = probability;
        }
    }

    return GDynamicDigitization::processTouchableImpl(std::move(gtouchable), thisStep);
}
