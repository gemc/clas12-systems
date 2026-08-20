#include "ft_trk.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <cmath>


int FTTRKDigitization::strip_id(double x_mm, double y_mm) {
    const double radius = std::hypot(x_mm, y_mm);
    if (radius <= RMIN_MM || radius >= RMAX_MM ||
        std::abs(y_mm) >= PITCH_MM * NSTRIPS * 2.0 / 6.0) {
        return -1;
    }

    int strip = static_cast<int>(std::floor(y_mm / PITCH_MM)) + 1 + NSTRIPS * 2 / 6;
    if (strip > NSTRIPS * 3 / 6) {
        strip += NSTRIPS * 2 / 6;
    } else if (strip > NSTRIPS / 6 && x_mm > 0) {
        strip += NSTRIPS * 2 / 6;
    }
    return strip;
}


std::vector<std::pair<int, double>> FTTRKDigitization::strip_weights(
    int layerIndex, const G4ThreeVector& localPosition, double energyDeposit,
    const std::vector<double>& dimensions) {
    using namespace CLHEP;

    if (dimensions.size() < 3) return {{-1, 1.0}};

    const double x = localPosition.x() / mm;
    const double y = localPosition.y() / mm;
    const double z = localPosition.z();
    const double radius = std::hypot(x, y);
    if (radius <= RMIN_MM || radius >= RMAX_MM) return {{-1, 1.0}};

    double xReal = x;
    double yReal = y;
    if (layerIndex % 2 == 0) {
        xReal = y;
        yReal = x;
    }

    const double z0 = -dimensions[2];
    const double driftHeight = 2.0 * dimensions[2];
    if (driftHeight <= 0) return {{-1, 1.0}};

    const double sigmaMax = 0.3 * mm * std::sqrt(driftHeight / cm);
    const double sigma = sigmaMax * std::sqrt(std::abs(z - z0) / driftHeight);
    const double yClosest = PITCH_MM * std::floor(yReal / PITCH_MM) + PITCH_MM / 2.0;
    const int electrons = static_cast<int>((energyDeposit / MeV) * 1.0E6 / IONIZATION_ENERGY_EV);

    std::vector<std::pair<int, double>> result;
    double totalWeight = 0.0;
    for (int offset = -N_SIGMA; offset <= N_SIGMA; ++offset) {
        const double stripY = yClosest + offset * PITCH_MM;
        const int strip = strip_id(xReal, stripY);
        if (strip <= 0) continue;

        double weight = offset == 0 && sigma == 0 ? 1.0 :
                        std::exp(-std::pow((stripY - yReal) * mm, 2) / (2.0 * sigma * sigma));
        const int weightedElectrons = static_cast<int>(std::lround(weight * electrons * 10.0));
        if (weightedElectrons > 0 || offset == 0) {
            result.emplace_back(strip, weight);
            totalWeight += weight;
        }
    }

    if (result.empty() || totalWeight <= 0) return {{-1, 1.0}};
    for (auto& [strip, weight] : result) weight /= totalWeight;
    return result;
}


std::vector<std::shared_ptr<GTouchable>> FTTRKDigitization::processTouchableImpl(
    std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) {
    const auto identity = gtouchable->getIdentity();
    if (identity.size() <= STRIP_INDEX) return {};

    const int layer = 2 * identity[0].getValue() + identity[1].getValue() - 2;
    const auto transform = thisStep->GetPreStepPoint()->GetTouchableHandle()->GetHistory()->GetTopTransform();
    const auto localPosition = transform.TransformPoint(thisStep->GetPostStepPoint()->GetPosition());
    const auto weights = strip_weights(layer - 1, localPosition, thisStep->GetTotalEnergyDeposit(),
                                       gtouchable->getDetectorDimensions());
    const auto binned = GDynamicDigitization::processTouchableImpl(std::move(gtouchable), thisStep);

    std::vector<std::shared_ptr<GTouchable>> result;
    result.reserve(binned.size() * weights.size());
    for (const auto& timeCell : binned) {
        for (const auto& [strip, weight] : weights) {
            auto stripTouchable = std::make_shared<GTouchable>(*timeCell);
            stripTouchable->setIdentityValue(STRIP_INDEX, strip);
            result.push_back(std::move(stripTouchable));
        }
    }
    return result;
}
