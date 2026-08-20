#pragma once

// gemc
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// fthodo plugin
#include "ft_hodo_constants.h"

// c++
#include <memory>
#include <string>


class FTHODODigitization : public GDynamicDigitization {
public:
    explicit FTHODODigitization(const std::shared_ptr<GOptions>& g) : GDynamicDigitization(g) {
        log = std::make_shared<GLogger>(g, "FTHODODigitization", "ft_hodo");
    }

    bool defineReadoutSpecsImpl() override;
    bool loadConstantsImpl(int runno, std::string const& variation) override;
    bool loadTTImpl(int runno, std::string const& variation) override;

    [[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, size_t hitn) override;

    FTHODOConstants constants;

private:
    bool accountForHardwareStatus = false;

    static constexpr double FADC_PRECISION = 0.0625;

    [[nodiscard]] static double convert_to_precision(double time) {
        return static_cast<int>(time / FADC_PRECISION) * FADC_PRECISION;
    }
};
