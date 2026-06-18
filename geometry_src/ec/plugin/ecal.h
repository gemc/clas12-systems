#pragma once

// gemc
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// ecal plugin
#include "ecal_constants.h"

// c++
#include <memory>
#include <string>


class ECAL_digitization : public GDynamicDigitization {
public:
    explicit ECAL_digitization(const std::shared_ptr<GOptions>& g) : GDynamicDigitization(g) {
        log = std::make_shared<GLogger>(g, "ECAL_digitization", "ecal");
    }

    bool defineReadoutSpecsImpl() override;

    [[nodiscard]] std::vector<std::shared_ptr<GTouchable>> processTouchableImpl(
        std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) override;

    bool loadConstantsImpl(int runno, std::string const& variation) override;
    bool loadTTImpl(int runno, std::string const& variation) override;

    [[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, size_t hitn) override;

    ECALConstants ecc;

private:
    bool accountForHardwareStatus = false;

    double fadc_precision = 0.0625;

    [[nodiscard]] double convert_to_precision(double time) const {
        return static_cast<int>(time / fadc_precision) * fadc_precision;
    }

    [[nodiscard]] static double getTRES(double x, double p0, double p1, double p2, double p3);
};
