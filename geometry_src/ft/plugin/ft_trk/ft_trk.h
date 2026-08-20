#pragma once

// gemc
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// c++
#include <memory>
#include <string>
#include <utility>
#include <vector>


class FTTRKDigitization : public GDynamicDigitization {
public:
    explicit FTTRKDigitization(const std::shared_ptr<GOptions>& g) : GDynamicDigitization(g) {
        log = std::make_shared<GLogger>(g, "FTTRKDigitization", "ft_trk");
    }

    bool defineReadoutSpecsImpl() override;

    [[nodiscard]] std::vector<std::shared_ptr<GTouchable>> processTouchableImpl(
        std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) override;

    [[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, size_t hitn) override;

private:
    static constexpr double IONIZATION_ENERGY_EV = 25.0;
    static constexpr double RMIN_MM = 70.43;
    static constexpr double RMAX_MM = 143.66;
    static constexpr double PITCH_MM = 0.560;
    static constexpr int NSTRIPS = 768;
    static constexpr int N_SIGMA = 4;
    static constexpr size_t STRIP_INDEX = 3;

    [[nodiscard]] static int strip_id(double x_mm, double y_mm);
    [[nodiscard]] static std::vector<std::pair<int, double>> strip_weights(
        int layerIndex, const G4ThreeVector& localPosition, double energyDeposit,
        const std::vector<double>& dimensions);
};
