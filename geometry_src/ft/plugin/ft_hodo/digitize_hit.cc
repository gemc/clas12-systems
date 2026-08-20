#include "ft_hodo.h"

// geant4
#include "G4Poisson.hh"

// CLHEP
#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>


namespace {

template <typename T>
bool has_channel(const std::vector<T>& values, int component) {
    return component >= 1 && values.size() >= static_cast<size_t>(component);
}

} // namespace


std::unique_ptr<GDigitizedData> FTHODODigitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& identity = ghit->getGID();
    if (identity.size() < 3 || ghit->nsteps() == 0) return nullptr;

    const int sector = identity[0].getValue();
    const int layer = identity[1].getValue();
    const int component = identity[2].getValue();
    if (sector < 1 || sector > FTHODOConstants::NSECTOR ||
        layer < 1 || layer > FTHODOConstants::NLAYER || component < 1) {
        return nullptr;
    }

    const int sectorIndex = sector - 1;
    const int layerIndex = layer - 1;
    const int componentIndex = component - 1;
    if (!has_channel(constants.gain_pc[sectorIndex][layerIndex], component) ||
        !has_channel(constants.mips_charge[sectorIndex][layerIndex], component) ||
        !has_channel(constants.mips_energy[sectorIndex][layerIndex], component) ||
        !has_channel(constants.time_offset[sectorIndex][layerIndex], component) ||
        !has_channel(constants.time_rms[sectorIndex][layerIndex], component)) {
        return nullptr;
    }

    const double mipsEnergy = constants.mips_energy[sectorIndex][layerIndex][componentIndex];
    const double gain = constants.gain_pc[sectorIndex][layerIndex][componentIndex];
    if (mipsEnergy == 0 || gain == 0 || constants.ns_per_sample == 0) return nullptr;

    int adc = 0;
    double fadcTime = 8191.0;
    const double totalEnergy = ghit->getTotalEnergyDeposited();

    if (totalEnergy > 0) {
        fadcTime = ghit->getAverageTime() + constants.time_offset[sectorIndex][layerIndex][componentIndex] +
                   CLHEP::RandGauss::shoot(0.0, constants.time_rms[sectorIndex][layerIndex][componentIndex]);

        double charge = totalEnergy * constants.mips_charge[sectorIndex][layerIndex][componentIndex] /
                        mipsEnergy;
        const double npeMean = charge / gain;
        if (npeMean > 0) charge *= G4Poisson(npeMean) / npeMean;

        adc = static_cast<int>(charge * constants.fadc_input_impedance / constants.fadc_lsb /
                               constants.ns_per_sample);
    }

    if (accountForHardwareStatus && has_channel(constants.status[sectorIndex][layerIndex], component)) {
        const int status = constants.status[sectorIndex][layerIndex][componentIndex];
        if (status == 3) {
            adc = 0;
            fadcTime = 0;
        } else if (status != 0 && status != 1 && status != 5) {
            log->warning("Unknown FTHODO status ", status, " for sector/layer/component ", sector, "/", layer,
                         "/", component);
        }
    }

    auto digitized = std::make_unique<GDigitizedData>(gopts, ghit);
    digitized->includeVariable("hitn", static_cast<int>(hitn));
    digitized->includeVariable("sector", sector);
    digitized->includeVariable("layer", layer);
    digitized->includeVariable("component", component);
    digitized->includeVariable("ADC_order", 0);
    digitized->includeVariable("ADC_ADC", adc);
    digitized->includeVariable("ADC_time", convert_to_precision(fadcTime / ns));
    digitized->includeVariable("ADC_ped", 0);
    return digitized;
}
