// dc plugin
#include "dc.h"

// geant4
#include "G4Step.hh"
#include "G4ThreeVector.hh"

// c++
#include <cmath>

namespace {

constexpr int NWIRES  = 112;
constexpr int NLAYERS = 6;

bool valid_dc_touchable(const std::shared_ptr<GTouchable>& gtouchable) {
    if (gtouchable == nullptr) return false;

    const auto identity = gtouchable->getIdentity();
    const auto dims     = gtouchable->getDetectorDimensions();

    return identity.size() > 3 &&
           dims.size() > 3 &&
           std::isfinite(dims[0]) &&
           std::isfinite(dims[3]) &&
           dims[0] > 0.0 &&
           dims[3] > 0.0;
}

// Returns the local (y, z) position of the sense wire centre in the superlayer frame.
// Wire positions are staggered by half a pitch on odd layers.
G4ThreeVector dc_wire_position(int layer, int wire, double dlayer, double dwire) {
    return G4ThreeVector(0.0, dwire * (static_cast<double>(wire) + 0.5 * (layer % 2)), dlayer * layer);
}

// Distance-of-closest-approach from a local-frame hit point to a sense wire.
double dc_doca(const G4ThreeVector& pos, int layer, int wire, double dlayer, double dwire) {
    G4ThreeVector w = dc_wire_position(layer, wire, dlayer, dwire);
    return std::sqrt(std::pow(pos.y() - w.y(), 2.0) + std::pow(pos.z() - w.z(), 2.0));
}

} // namespace


// Determine the sense wire (layer, wire) from the step hit position and update the touchable
// identity, then delegate to the base class for time-cell binning.
//
// Ported from dc_HitProcess::processID in clas12Tags.
// identity[2] = layer (1-6), identity[3] = wire (1-112); -1 when the hit falls outside.
std::vector<std::shared_ptr<GTouchable>> DC_digitization::processTouchableImpl(
    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) {

    if (!valid_dc_touchable(gtouchable) || thisStep == nullptr) return {};

    const auto* preStep  = thisStep->GetPreStepPoint();
    const auto* postStep = thisStep->GetPostStepPoint();
    if (preStep == nullptr || postStep == nullptr) return {};

    const auto touchableHandle = preStep->GetTouchableHandle();
    if (!touchableHandle || touchableHandle->GetHistory() == nullptr) return {};

    const auto&  dims    = gtouchable->getDetectorDimensions();
    const double zlength = dims[0]; // G4Trap half-thickness along z (wire-depth direction)
    const double ylength = dims[3]; // G4Trap semiheight along y (wire-number direction)

    // Wire-plane pitch: the superlayer volume spans NLAYERS+1 guard/sense plane triplets
    const double deltaz = 2.0 * zlength / 3.0 / static_cast<double>(NLAYERS + 1);
    const double deltay = 2.0 * ylength / static_cast<double>(NWIRES + 1) / 2.0;
    const double dlayer = 3.0 * deltaz;
    const double dwire  = 2.0 * deltay;

    // Transform the global post-step position into the superlayer local frame
    G4ThreeVector xyz  = postStep->GetPosition();
    G4ThreeVector Lxyz = touchableHandle->GetHistory()->GetTopTransform().TransformPoint(xyz);

    const double loc_z  = Lxyz.z() + zlength;
    const double loc_y  = Lxyz.y() + ylength;
    const int    ilayer = static_cast<int>(std::floor(loc_z / deltaz)); // 0..3*(NLAYERS+1)
    const int    iwire  = static_cast<int>(std::floor(loc_y / deltay)); // 0..2*(NWIRES+1)

    int nlayer = -1;
    int nwire  = -1;

    if (ilayer % 3 != 1) {
        // Hit lies between the two field wires flanking a sense wire: layer is unambiguous
        nlayer = static_cast<int>(std::floor(static_cast<double>(ilayer - 1) / 3.0)) + 1;
    } else {
        // Hit is in the gap between adjacent sense-wire planes — use DOCA to resolve
        const int nl1 = ilayer / 3;
        const int nw1 = static_cast<int>(std::floor(static_cast<double>(iwire - 1 - nl1 % 2) / 2.0)) + 1;
        const int nl2 = ilayer / 3 + 1;
        const int nw2 = static_cast<int>(std::floor(static_cast<double>(iwire - 1 - nl2 % 2) / 2.0)) + 1;

        G4ThreeVector local(0.0, Lxyz.y() + ylength, Lxyz.z() + zlength);
        const double d1 = dc_doca(local, nl1, nw1, dlayer, dwire);
        const double d2 = dc_doca(local, nl2, nw2, dlayer, dwire);
        nlayer = (d1 < d2) ? nl1 : nl2;
    }

    if (nlayer > 0 && nlayer < NLAYERS + 1)
        nwire = static_cast<int>(std::floor(static_cast<double>(iwire - 1 - nlayer % 2) / 2.0)) + 1;

    if (nwire  < 1 || nwire  > NWIRES)  nwire  = -1;
    if (nlayer < 1 || nlayer > NLAYERS) nlayer = -1;

    gtouchable->setIdentityValue(2, nlayer);
    gtouchable->setIdentityValue(3, nwire);

    return GDynamicDigitization::processTouchableImpl(std::move(gtouchable), thisStep);
}
