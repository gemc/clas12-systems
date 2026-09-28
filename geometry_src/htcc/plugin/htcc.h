#pragma once

// gemc
#include "gemc/gdynamicDigitization/gdynamicdigitization.h"

// htcc plugin
#include "htcc_constants.h"

// geant4
#include "G4Step.hh"

// c++
#include <map>
#include <memory>
#include <string>
#include <tuple>
#include <vector>


class HTCC_digitization : public GDynamicDigitization {
public:
    explicit HTCC_digitization(const std::shared_ptr<GOptions>& g) : GDynamicDigitization(g) {
        log = std::make_shared<GLogger>(g, "HTCC_digitization", "htcc");
    }

    bool defineReadoutSpecsImpl() override;

    [[nodiscard]] std::vector<std::shared_ptr<GTouchable>> processTouchableImpl(
        std::shared_ptr<GTouchable> gtouchable, G4Step* thisStep) override;

    bool loadConstantsImpl(int runno, std::string const& variation) override;
    bool loadTTImpl(int runno, std::string const& variation) override;

    [[nodiscard]] std::unique_ptr<GDigitizedData> digitizeHitImpl(GHit* ghit, size_t hitn) override;
    [[nodiscard]] bool apply_thresholds_impl(GHit* ghit, GDigitizedData* digitizedData) override;
    [[nodiscard]] bool apply_efficiency_impl(GHit* ghit, GDigitizedData* digitizedData) override;

    bool decisionToSkipHit(double energy, const G4Step* thisStep) override;
    [[nodiscard]] bool shouldStopTrackAfterHitImpl(const G4Step* thisStep) const override;

    HTCCConstants htccc;

private:
    // (sector, ring, half, trackId): the geometry identity order is sector, ring, half.
    using PhotonKey = std::tuple<int, int, int, int>;

    double fadc_precision = 0.0625;  // 62.5 ps FADC resolution
    inline static thread_local std::map<PhotonKey, double> photonDetectionProbability;

    [[nodiscard]] double convert_to_precision(double time) const {
        return static_cast<int>(time / fadc_precision) * fadc_precision;
    }

    [[nodiscard]] static bool valid_index(int sector, int ring, int half);
    [[nodiscard]] static PhotonKey photon_key(const std::vector<GIdentifier>& gid, int trackId);
};
