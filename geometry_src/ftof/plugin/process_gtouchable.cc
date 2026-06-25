#include "ftof.h"


// Each FTOF paddle is read out at both ends. The geometry declares the touchable with side = 0
// (Left PMT); here we run the base-class time-cell binning and then, for every resulting touchable,
// emit a sibling with side = 1 (Right PMT). This mirrors the clas12Tags `ftof_HitProcess::processID`
// which duplicates the hit identifier with the PMT-side index toggled.
std::vector<std::shared_ptr<GTouchable>> FTOF_digitization::processTouchableImpl(
    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) {

    auto binned = GDynamicDigitization::processTouchableImpl(std::move(gtouchable), thisStep);

    std::vector<std::shared_ptr<GTouchable>> result;
    result.reserve(binned.size() * 2);

    for (const auto& left : binned) {
        result.push_back(left);                                  // side 0 (Left PMT)
        auto right = std::make_shared<GTouchable>(*left);        // copy identity + time cell
        right->setIdentityValue(SIDE_INDEX, 1);                  // side 1 (Right PMT)
        result.push_back(right);
    }

    return result;
}
