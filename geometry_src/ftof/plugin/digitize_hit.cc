#include "ftof.h"

// geant4
#include "G4Poisson.hh"
#include "Randomize.hh"

// CLHEP
#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <cmath>


namespace {

bool valid_index(const FTOFConstants& ftc, int sector, int panel, int paddle, int side) {
    if (sector < 1 || sector > FTOFConstants::NSECT) return false;
    if (panel  < 1 || panel  > FTOFConstants::NPANEL) return false;
    if (side   < 0 || side   > 1) return false;
    if (paddle < 1 || paddle > ftc.npaddles[panel - 1]) return false;
    return true;
}

// All per-paddle constants used by the digitization must have an entry for this paddle.
bool has_paddle_constants(const FTOFConstants& ftc, int s, int p, int side, int paddle) {
    const auto idx = static_cast<size_t>(paddle);
    return ftc.attlen[s][p][side].size() >= idx &&
           ftc.attlen[s][p][1 - side].size() >= idx &&
           ftc.veff[s][p][side].size() >= idx &&
           ftc.tdcconv[s][p][side].size() >= idx &&
           ftc.adcoffset[s][p][side].size() >= idx &&
           ftc.countsForMIP[s][p][side].size() >= idx &&
           ftc.threshold[s][p][side].size() >= idx &&
           ftc.efficiency[s][p][side].size() >= idx &&
           ftc.twlk[s][p][3 * side + 1].size() >= idx &&
           ftc.twlke[s][p][3].size() >= idx &&
           ftc.twlkp[s][p][1].size() >= idx &&
           ftc.toff_LR[s][p].size() >= idx &&
           ftc.toff_RFpad[s][p].size() >= idx &&
           ftc.toff_P2P[s][p].size() >= idx &&
           ftc.tres[s][p].size() >= idx;
}

} // namespace


std::unique_ptr<GDigitizedData> FTOF_digitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& gid = ghit->getGID();
    if (gid.size() < 4 || ghit->nsteps() == 0) return nullptr;

    const int sector = gid[0].getValue();
    const int panel  = gid[1].getValue();   // 1 = 1A, 2 = 1B, 3 = 2
    const int paddle = gid[2].getValue();
    const int pmt    = gid[3].getValue();    // 0 = Left PMT, 1 = Right PMT

    if (!valid_index(ftc, sector, panel, paddle, pmt)) return nullptr;

    const int secI = sector - 1;
    const int panI = panel - 1;
    const int padI = paddle - 1;

    if (!has_paddle_constants(ftc, secI, panI, pmt, paddle)) return nullptr;

    const double adcoffset = ftc.adcoffset[secI][panI][pmt][padI];
    const double tdcconv   = ftc.tdcconv[secI][panI][pmt][padI];

    double tdc_jitter = 0;
    if (ftc.jitter_cycles != 0) {
        tdc_jitter = ftc.jitter_period * static_cast<double>((0 + ftc.jitter_phase) % ftc.jitter_cycles);
    }

    // paddle half-length (G4Box dx) and energy-weighted average local x
    const auto& dims = ghit->getDetectorDimensions();
    if (dims.empty()) return nullptr;
    const double length = dims[0];
    const double lx     = ghit->getAvgLocalPosition().x();

    // distance to this PMT end
    const double d = length + (1 - 2 * pmt) * lx;

    const double attlen           = ftc.attlen[secI][panI][pmt][padI];
    const double attlen_otherside = ftc.attlen[secI][panI][1 - pmt][padI];

    const double att  = std::exp(-d / cm / attlen);
    const double gain = std::sqrt(std::exp(-d / cm / attlen) *
                                  std::exp(-(2 * length - d) / cm / attlen_otherside));

    double energyDepositedAttenuated = ghit->getTotalEnergyDeposited() * att;
    if (ghit->getPid() == 0) {
        // geantinos deposit no energy; use momentum as a proxy, as in clas12Tags
        energyDepositedAttenuated = ghit->getMomentum().mag() / GeV * att;
    }

    const double time = ghit->getAverageTime();

    double adc = 0;
    int    tdc = 0;
    double time_in_ns = 0;

    const double nphe = G4Poisson(energyDepositedAttenuated * ftc.pmtPEYld);
    const double ene  = nphe / ftc.pmtPEYld;

    if (ene > 0) {
        adc = ene * ftc.countsForMIP[secI][panI][pmt][padI] / ftc.dEMIP[panI] / gain;

        const double A  = ftc.twlk[secI][panI][3 * pmt + 0][padI];
        const double B  = ftc.twlk[secI][panI][3 * pmt + 1][padI];
        const double E0 = ftc.twlke[secI][panI][0][padI];
        const double E1 = ftc.twlke[secI][panI][1][padI];
        const double E2 = ftc.twlke[secI][panI][2][padI];
        const double E3 = ftc.twlke[secI][panI][3][padI];
        const double P1 = ftc.twlkp[secI][panI][0][padI];
        const double P2 = ftc.twlkp[secI][panI][1][padI];

        const double eTot_MeV = ghit->getTotalEnergyDeposited() / MeV;

        const double timeWalk  = (1 - E0) * A / std::pow(adc, B);
        const double timeWalkE = E0 * E1 * std::exp(E2 * eTot_MeV) + E3 / eTot_MeV;
        const double timeWalkP = P1 * std::pow(lx / cm, 2) + P2 * lx / cm;

        double tU = time + d / ftc.veff[secI][panI][pmt][padI] / cm
                    + (1. - 2. * pmt) * ftc.toff_LR[secI][panI][padI] / 2.
                    - ftc.toff_RFpad[secI][panI][padI];
        tU -= ftc.toff_P2P[secI][panI][padI];

        time_in_ns = CLHEP::RandGauss::shoot(tU + timeWalk + timeWalkE - timeWalkP,
                                             std::sqrt(2.) * ftc.tres[secI][panI][padI]);
        tdc = static_cast<int>((time_in_ns + tdc_jitter) / tdcconv);
    }

    if (accountForHardwareStatus && ftc.status[secI][panI][pmt].size() > static_cast<size_t>(padI)) {
        switch (ftc.status[secI][panI][pmt][padI]) {
            case 0:
                break;
            case 1:
                adc = 0;
                break;
            case 2:
                tdc = 0;
                break;
            case 3:
                adc = tdc = 0;
                break;
            case 5:
                break;
            default:
                log->warning("Unknown FTOF status ", ftc.status[secI][panI][pmt][padI], " for sector ", sector,
                             ", panel ", panel, ", paddle ", paddle);
        }
    }

    const double fadc_time = convert_to_precision(time_in_ns - adcoffset);

    // Threshold and efficiency rejection is applied after digitization by the framework via
    // decisionToSkipDigitizedHitImpl(), gated by the -applyThresholds / -applyInefficiencies
    // options (both off by default, matching clas12Tags).

    auto digitizedData = std::make_unique<GDigitizedData>(gopts, ghit);
    digitizedData->includeVariable("hitn", static_cast<int>(hitn));
    digitizedData->includeVariable("sector", sector);
    digitizedData->includeVariable("layer", panel);
    digitizedData->includeVariable("component", paddle);
    digitizedData->includeVariable("ADC_order", pmt);
    digitizedData->includeVariable("ADC_ADC", static_cast<int>(adc));
    digitizedData->includeVariable("ADC_time", fadc_time);
    digitizedData->includeVariable("ADC_ped", 0);
    digitizedData->includeVariable("TDC_order", pmt + 2);
    digitizedData->includeVariable("TDC_TDC", tdc);

    return digitizedData;
}


bool FTOF_digitization::apply_thresholds_impl(GHit* ghit, const GDigitizedData* /*digitizedData*/) {
    using namespace CLHEP;

    // Raw output keeps every hit.
    if (ftc.outputRAW != 0) return false;

    // The framework only calls this for hits that digitizeHitImpl already accepted, so the
    // identity and per-paddle constants are valid here.
    const auto& gid = ghit->getGID();
    const int pmt  = gid[3].getValue();
    const int secI = gid[0].getValue() - 1;
    const int panI = gid[1].getValue() - 1;
    const int padI = gid[2].getValue() - 1;

    // Attenuated energy at this PMT end, recomputed deterministically as in digitizeHitImpl.
    const double length = ghit->getDetectorDimensions()[0];
    const double lx     = ghit->getAvgLocalPosition().x();
    const double d      = length + (1 - 2 * pmt) * lx;
    const double att    = std::exp(-d / cm / ftc.attlen[secI][panI][pmt][padI]);

    double energyDepositedAttenuated = ghit->getTotalEnergyDeposited() * att;
    if (ghit->getPid() == 0) {
        energyDepositedAttenuated = ghit->getMomentum().mag() / GeV * att;
    }

    return energyDepositedAttenuated < ftc.threshold[secI][panI][pmt][padI];
}


bool FTOF_digitization::apply_efficiency_impl(GHit* ghit, const GDigitizedData* /*digitizedData*/) {
    if (ftc.outputRAW != 0) return false;

    const auto& gid = ghit->getGID();
    const int pmt  = gid[3].getValue();
    const int secI = gid[0].getValue() - 1;
    const int panI = gid[1].getValue() - 1;
    const int padI = gid[2].getValue() - 1;

    return G4UniformRand() > ftc.efficiency[secI][panI][pmt][padI];
}
