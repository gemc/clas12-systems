#pragma once

#include <gemc/gstreamer/sro/gSROData.h>
#include <gemc/gparticle/gparticle_options.h>
#include <gemc/goptions/goptions.h>
#include <cmath>
#include <limits>
#include <stdexcept>

namespace ftcal_sro {

// Both the implementation and worker use this clock. Production spacing must be explicitly configured.
struct Clock {
    GSROTime spacing;
    GSROTime minimum_signal_time;

    GSROTime event_start(GSROEventId id) const {
        const auto maximum = std::numeric_limits<std::int64_t>::max() - 65536;
        if (id > static_cast<std::uint64_t>(maximum / spacing.count())) {
            throw std::overflow_error("FTCAL SRO event time overflow");
        }
        return spacing * static_cast<std::int64_t>(id);
    }
};

inline Clock clock_from_options(const std::shared_ptr<GOptions>& options) {
    const double spacing = gparticle::getEventTimeWidth(options);
    const double minimum = options->getRequiredScalarDouble("ft_cal_sro_min_signal_time");
    if (!std::isfinite(spacing) || spacing < 1 || spacing > 1e12 || std::floor(spacing) != spacing ||
        !std::isfinite(minimum) || minimum > 0 || minimum < -1e12 || std::floor(minimum) != minimum) {
        throw std::invalid_argument("FTCAL SRO requires integral eventTimeWidth in [1, 1e12] ns and "
                                    "a minimum signal time in [-1e12, 0] ns");
    }
    return {GSROTime{static_cast<std::int64_t>(spacing)}, GSROTime{static_cast<std::int64_t>(minimum)}};
}

} // namespace ftcal_sro
