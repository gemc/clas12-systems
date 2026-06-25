#pragma once

// gemc
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// ftof plugin
#include "ftof_constants.h"

// c++
#include <memory>
#include <string>
#include <vector>


class FTOF_digitization : public GDynamicDigitization {
public:
    explicit FTOF_digitization(const std::shared_ptr<GOptions>& g) : GDynamicDigitization(g) {
        log = std::make_shared<GLogger>(g, "FTOF_digitization", "ftof");
    }

    bool defineReadoutSpecsImpl() override;

    // FTOF reads out both PMT ends, so each step touchable is split into a Left (side 0) and a
    // Right (side 1) readout channel, mirroring the clas12Tags `processID` duplication.
    [[nodiscard]] std::vector<std::shared_ptr<GTouchable>> processTouchableImpl(
        std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) override;

    bool loadConstantsImpl(int runno, std::string const& variation) override;
    bool loadTTImpl(int runno, std::string const& variation) override;

    [[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, size_t hitn) override;

    FTOFConstants ftc;

private:
    bool accountForHardwareStatus = false;

    // index of the "side" identifier (sector, panel, paddle, side) declared by the geometry
    static constexpr size_t SIDE_INDEX = 3;

    double fadc_precision = 0.0625;  // 62.5 ps resolution

    [[nodiscard]] double convert_to_precision(double time) const {
        return static_cast<int>(time / fadc_precision) * fadc_precision;
    }
};
