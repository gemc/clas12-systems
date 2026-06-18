#include "ecal.h"


std::vector<std::shared_ptr<GTouchable>> ECAL_digitization::processTouchableImpl(
    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) {

    return GDynamicDigitization::processTouchableImpl(std::move(gtouchable), thisStep);
}
