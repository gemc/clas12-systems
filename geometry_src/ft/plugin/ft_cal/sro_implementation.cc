#include <gemc/gstreamer/sro/gSROImplementation.h>
#include "sro_timing.h"
#include "sro/jlab_sro.h"

namespace {

class Timing final : public GSROTiming {
public:
    explicit Timing(ftcal_sro::Clock value) : clock(value) {}
    std::optional<GSROTime> earliest_remaining_time(GSROEventId first) const override {
        return clock.event_start(first) + clock.minimum_signal_time;
    }
private:
    ftcal_sro::Clock clock;
};

class Implementation final : public GSROImplementation {
public:
    using GSROImplementation::GSROImplementation;
    GSROConfiguration configure_run(const GSRORunContext& run) override {
        const auto clock = ftcal_sro::clock_from_options(options);
        clock.event_start(run.event_count); // Reject an overflowing timeline before any worker starts.
        return {std::make_shared<Timing>(clock), {}, 65536};
    }
    GSROCrateResources create_crate(GSROCrateId crate, const GSRORunContext& run) const override {
        return clas12::sro::create_crate(crate, run.output_basename + "_r" + std::to_string(run.run_id) +
                                       "_crate" + std::to_string(crate) + ".ev");
    }
};

} // namespace

extern "C" GSROImplementation* GSROImplementationFactory(const std::shared_ptr<GOptions>& options) {
    return new Implementation(options);
}
