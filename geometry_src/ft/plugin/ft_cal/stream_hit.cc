#include "ft_cal.h"
#include "sro_timing.h"
#include "sro/jlab_sro.h"

#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>
#include <algorithm>
#include <cmath>
#include <stdexcept>

void FTCALDigitization::stream_hit(GHit* hit, std::size_t, const GSROEventContext& event,
                                  const GSROEmit& emit) const {
    const auto identity = hit->getTTID();
    const auto& dimensions = hit->getDetectorDimensions();
    if (identity.size() != 2 || identity[0] < 1 || identity[0] > 22 || identity[1] < 1 || identity[1] > 22 ||
        dimensions.size() < 3 || hit->nsteps() == 0) {
        throw std::invalid_argument("FTCAL SRO requires a crystal hit with {ix, iy} identity");
    }
    const int crystal = (identity[1] - 1) * 22 + identity[0] - 1;
    if (!translationTable) { throw std::logic_error("FTCAL SRO translation table was not loaded"); }
    const auto address = translationTable->getElectronics(identity).getHAddress();
    if (address[0] > 255 || address[1] > 15 || address[2] > 15) {
        throw std::invalid_argument("FTCAL TT address exceeds the legacy JLAB SRO format");
    }
    if (accountForHardwareStatus && constants.status[crystal] == 3) { return; }
    const double energy = hit->getTotalEnergyDeposited();
    if (energy <= 0) { return; }
    if (constants.mips_energy[crystal] <= 0 || constants.fadc_to_charge[crystal] <= 0 ||
        constants.light_speed <= 0) {
        throw std::runtime_error("FTCAL SRO requires positive charge calibration and light speed");
    }
    // The integral charge follows digitizeHitImpl. Its APD noise draws do not affect the published ADC.
    const double adc = energy * constants.mips_charge[crystal] /
                       constants.mips_energy[crystal] / constants.fadc_to_charge[crystal];
    if (!std::isfinite(adc) || adc < 0) { throw std::runtime_error("Invalid FTCAL SRO charge"); }
    const auto charge = static_cast<std::uint32_t>(std::min(adc, 8191.0)); // Explicit 13-bit saturation.
    const double distance = dimensions[2] - hit->getAvgLocalPosition().z();
    const double signal_ns = (hit->getAverageTime() + distance / constants.light_speed +
                              constants.time_offset[crystal] +
                              CLHEP::RandGauss::shoot(0.0, constants.time_rms[crystal])) / CLHEP::ns;
    const auto clock = ftcal_sro::clock_from_options(gopts);
    // Gaussian tails/negative generator times cannot silently invalidate an already published time bound.
    if (!std::isfinite(signal_ns) || signal_ns < clock.minimum_signal_time.count() || signal_ns > 1e12) {
        throw std::runtime_error("FTCAL SRO signal time violates its configured bound; adjust "
                                 "ft_cal_sro_min_signal_time or the input/calibration timing");
    }
    const auto start = clock.event_start(event.event_id);
    const auto signal = static_cast<std::int64_t>(std::floor(signal_ns));
    if (signal > 0 && start.count() > std::numeric_limits<std::int64_t>::max() - 65536 - signal) {
        throw std::overflow_error("FTCAL SRO signal time overflow");
    }
    const auto time = start + GSROTime{signal};
    if (time < GSROTime{0}) { return; } // Acquisition starts at zero; discard pre-acquisition signals.
    const auto relative = static_cast<std::uint32_t>((time % clas12::sro::frame_duration).count());
    emit(static_cast<GSROCrateId>(address[0]), time, std::make_unique<clas12::sro::IntegralPayload>(
        address[0], address[1], address[2], charge, relative));
}
