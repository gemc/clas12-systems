#include "ft_cal.h"

// geant4
#include "G4Poisson.hh"

// CLHEP
#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <algorithm>


std::unique_ptr<GDigitizedData> FTCALDigitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& identity = ghit->getGID();
    const auto& dimensions = ghit->getDetectorDimensions();
    if (identity.size() < 2 || dimensions.size() < 3 || ghit->nsteps() == 0) return nullptr;

    const int idx = identity[0].getValue();
    const int idy = identity[1].getValue();
    const int crystal = (idy - 1) * 22 + idx - 1;
    if (idx < 1 || idx > 22 || idy < 1 || idy > 22 || crystal < 0 ||
        crystal >= FTCALConstants::NCHANNEL) {
        return nullptr;
    }

    const double mipsEnergy = constants.mips_energy[crystal];
    const double fadcToCharge = constants.fadc_to_charge[crystal];
    if (mipsEnergy == 0 || fadcToCharge == 0) return nullptr;

    int adc = 0;
    double fadcTime = 8191.0;
    const double totalEnergy = ghit->getTotalEnergyDeposited();

    if (totalEnergy > 0) {
        const double length = 2.0 * dimensions[2];
        const double distance = length / 2.0 - ghit->getAvgLocalPosition().z();
        fadcTime = ghit->getAverageTime() + distance / constants.light_speed;
        fadcTime += constants.time_offset[crystal] +
                    CLHEP::RandGauss::shoot(0.0, constants.time_rms[crystal]);

        const double charge = totalEnergy * constants.mips_charge[crystal] / mipsEnergy;
        const double denominator = 1.6E-7 * constants.preamp_gain[crystal] * constants.apd_gain[crystal];
        if (denominator > 0) {
            const double npeMean = charge / denominator;
            const double npe = G4Poisson(npeMean);
            double electrons = npe * constants.apd_gain[crystal];
            electrons *= CLHEP::RandGauss::shoot(1.0, constants.apd_noise);
            electrons = std::max(0.0, electrons);
            electrons += constants.preamp_input_noise * CLHEP::RandGauss::shoot(0.0, 1.0);
            [[maybe_unused]] const double boundedElectrons = std::max(0.0, electrons);
        }
        adc = static_cast<int>(charge / fadcToCharge);
    }

    if (accountForHardwareStatus && constants.status[crystal] == 3) {
        adc = 0;
        fadcTime = 0;
    } else if (accountForHardwareStatus && constants.status[crystal] != 0 &&
               constants.status[crystal] != 1 && constants.status[crystal] != 5) {
        log->warning("Unknown FTCAL status ", constants.status[crystal], " for component ", crystal);
    }

    auto digitized = std::make_unique<GDigitizedData>(gopts, ghit);
    digitized->includeVariable("hitn", static_cast<int>(hitn));
    digitized->includeVariable("sector", 1);
    digitized->includeVariable("layer", 1);
    digitized->includeVariable("component", crystal);
    digitized->includeVariable("ADC_order", 0);
    digitized->includeVariable("ADC_ADC", adc);
    digitized->includeVariable("ADC_time", convert_to_precision(fadcTime / ns));
    digitized->includeVariable("ADC_ped", 0);
    return digitized;
}
