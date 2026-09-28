#include "htcc.h"

// geant4
#include "G4Material.hh"
#include "G4MaterialPropertiesTable.hh"
#include "G4MaterialPropertyVector.hh"
#include "G4OpticalPhoton.hh"


namespace {

bool is_optical_photon_step(const G4Step* step) {
    return step != nullptr && step->GetTrack() != nullptr &&
           step->GetTrack()->GetDefinition() == G4OpticalPhoton::OpticalPhotonDefinition();
}

} // namespace


bool HTCC_digitization::valid_index(int sector, int ring, int half) {
    return sector >= 1 && sector <= HTCCConstants::NSECT &&
           ring >= 1 && ring <= HTCCConstants::NRING &&
           half >= 1 && half <= HTCCConstants::NHALF;
}


HTCC_digitization::PhotonKey HTCC_digitization::photon_key(const std::vector<GIdentifier>& gid, int trackId) {
    return {gid[0].getValue(), gid[1].getValue(), gid[2].getValue(), trackId};
}


bool HTCC_digitization::decisionToSkipHit(double energy, const G4Step* thisStep) {
    if (thisStep == nullptr || thisStep->GetTrack() == nullptr) return true;

    if (is_optical_photon_step(thisStep)) return false;
    return GDynamicDigitization::decisionToSkipHit(energy);
}


bool HTCC_digitization::shouldStopTrackAfterHitImpl(const G4Step* thisStep) const {
    return is_optical_photon_step(thisStep);
}


// The photocathode quantum efficiency is read here, once per optical-photon step, from the PMT quartz
// material's EFFICIENCY property (clas12Tags htcc_hitprocess integrateDgt). The detection probability is
// cached by (identity, trackId) so digitizeHitImpl can accept/reject each unique photon.
std::vector<std::shared_ptr<GTouchable>> HTCC_digitization::processTouchableImpl(
    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) {

    if (is_optical_photon_step(thisStep)) {

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
