#include "ft_trk.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


std::unique_ptr<GDigitizedData> FTTRKDigitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& identity = ghit->getGID();
    if (identity.size() <= STRIP_INDEX || ghit->nsteps() == 0) return nullptr;

    const int layer = 2 * identity[0].getValue() + identity[1].getValue() - 2;
    const int targetStrip = identity[STRIP_INDEX].getValue();
    const auto& positions = ghit->getLocalPositions();
    const auto& energyDeposits = ghit->getEdeps();
    const auto& dimensions = ghit->getDetectorDimensions();

    double sharedEnergy = 0.0;
    for (size_t step = 0; step < ghit->nsteps(); ++step) {
        const auto weights = strip_weights(layer - 1, positions[step], energyDeposits[step], dimensions);
        for (const auto& [strip, weight] : weights) {
            if (strip == targetStrip) {
                sharedEnergy += energyDeposits[step] * weight;
                break;
            }
        }
    }

    const int adc = static_cast<int>(sharedEnergy / (IONIZATION_ENERGY_EV * eV));

    auto digitized = std::make_unique<GDigitizedData>(gopts, ghit);
    digitized->includeVariable("hitn", static_cast<int>(hitn));
    digitized->includeVariable("sector", 1);
    digitized->includeVariable("layer", layer);
    digitized->includeVariable("component", targetStrip);
    digitized->includeVariable("ADC_order", 0);
    digitized->includeVariable("ADC_ADC", adc);
    digitized->includeVariable("ADC_time", 0.0);
    digitized->includeVariable("ADC_ped", 0);
    digitized->includeVariable("ADC_integral", 0);
    digitized->includeVariable("ADC_timestamp", 0);
    return digitized;
}
