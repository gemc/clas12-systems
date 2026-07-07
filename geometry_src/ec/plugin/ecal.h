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
    [[nodiscard]] bool apply_thresholds_impl(GHit* ghit, GDigitizedData* digitizedData) override;
    [[nodiscard]] bool apply_efficiency_impl(GHit* ghit, GDigitizedData* digitizedData) override;
    [[nodiscard]] bool thresholds_are_intrinsic_impl() const override { return true; }
    [[nodiscard]] bool efficiencies_are_intrinsic_impl() const override { return true; }

    ECALConstants ecc;

private:
    bool accountForHardwareStatus = false;

    double fadc_precision = 0.0625;

    [[nodiscard]] double convert_to_precision(double time) const {
        return static_cast<int>(time / fadc_precision) * fadc_precision;
    }

    [[nodiscard]] static double getTRES(double x, double p0, double p1, double p2, double p3);

    // Transient digitization values used by post-digitization ECAL policies. They are internal
    // hand-off values, not output-bank variables: the callbacks use them to mirror clas12Tags
    // thresholds and DSC/TDC efficiency without repeating attenuation, timing, or ADC work.
    static constexpr const char* ECAL_UNROUNDED_ADC = "ecal_unrounded_adc";
    static constexpr const char* ECAL_DTIME_IN_NS = "ecal_dtime_in_ns";
};
