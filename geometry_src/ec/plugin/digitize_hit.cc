#include "ecal.h"

// geant4
#include "G4Poisson.hh"
#include "Randomize.hh"

// CLHEP
#include <CLHEP/Random/RandGauss.h>
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <cmath>
#include <vector>


namespace {

bool valid_index(int sector, int layer, int strip) {
    return sector >= 1 && sector <= ECALConstants::NSECT &&
           layer >= 1 && layer <= ECALConstants::NLAYER &&
           strip >= 1;
}

bool has_strip_constants(const ECALConstants& ecc, int sec, int lay, int strip) {
    return ecc.gain[sec][lay].size() > static_cast<size_t>(strip) &&
           ecc.attlen[sec][lay][4].size() > static_cast<size_t>(strip) &&
           ecc.ftime[sec][lay][6].size() > static_cast<size_t>(strip) &&
           ecc.dtime[sec][lay][8].size() > static_cast<size_t>(strip) &&
           ecc.fveff[sec][lay].size() > static_cast<size_t>(strip) &&
           ecc.dveff[sec][lay].size() > static_cast<size_t>(strip) &&
           ecc.deff[sec][lay][2].size() > static_cast<size_t>(strip) &&
           ecc.fthr[sec][lay].size() > static_cast<size_t>(strip) &&
           !ecc.fadc_offset[sec][lay].empty() &&
           !ecc.tmf_offset[sec][lay].empty() &&
           !ecc.global_time_walk[sec][lay].empty() &&
           !ecc.ftres[sec][lay][3].empty() &&
           !ecc.dtres[sec][lay][3].empty();
}

int ecal_view_from_layer(int layer) {
    int view = layer;
    if (layer > 3 && layer < 7) {
        view = layer - 3;
    } else if (layer >= 7) {
        view = layer - 6;
    }
    return view;
}

} // namespace


double ECAL_digitization::getTRES(double x, double p0, double p1, double p2, double p3) {
    return p0 * std::exp(std::pow(x, p3) / 120000.0) + p1 / x + p2 / std::pow(x, 0.5);
}


std::unique_ptr<GDigitizedData> ECAL_digitization::digitizeHitImpl(GHit* ghit, size_t hitn) {
    using namespace CLHEP;

    const auto& gid = ghit->getGID();
    if (gid.size() < 3 || ghit->nsteps() == 0) return nullptr;

    const int sector = gid[0].getValue();
    const int layer  = gid[1].getValue();
    const int strip  = gid[2].getValue();

    if (!valid_index(sector, layer, strip)) return nullptr;

    const int secI   = sector - 1;
    const int layerI = layer - 1;
    const int stripI = strip - 1;

    if (!has_strip_constants(ecc, secI, layerI, stripI)) return nullptr;

    const int  view   = ecal_view_from_layer(layer);
    const bool isPCAL = layer < 4;

    double pmtPEYld = 3.5;
    if (isPCAL) pmtPEYld = 11.5;

    const auto& dims = ghit->getDetectorDimensions();
    if (dims.size() <= 5) return nullptr;
    const double pDx2 = dims[5];

    const auto Lpos   = ghit->getLocalPositions();
    const auto Edep   = ghit->getEdeps();
    const auto times  = ghit->getTimes();
    const auto nsteps = ghit->nsteps();

    double ftime_in_ns     = 0;
    double dtime_in_ns     = 0;
    double ftime_in_ns_res = 0;
    double dtime_in_ns_res = 0;

    double Etota  = 0;
    double FTtota = 0;
    double DTtota = 0;

    const double A = ecc.attlen[secI][layerI][0][stripI];
    const double B = ecc.attlen[secI][layerI][1][stripI] * 10.0;
    const double C = ecc.attlen[secI][layerI][2][stripI];
    const double D = ecc.attlen[secI][layerI][3][stripI];
    const double E = ecc.attlen[secI][layerI][4][stripI] * 10.0;

    const double G   = ecc.gain[secI][layerI][stripI];
    const double tmf = ecc.tmf_offset[secI][layerI][stripI];
    const double fo  = ecc.fadc_offset[secI][layerI][0];
    const double gtw = ecc.global_time_walk[secI][layerI][0];

    const double FTOFFSET = ecc.fadc_global_offset;
    const double tgo      = ecc.tdc_global_offset;

    const double fa0 = ecc.ftime[secI][layerI][0][stripI];
    const double fa2 = ecc.ftime[secI][layerI][2][stripI];
    const double fa3 = ecc.ftime[secI][layerI][3][stripI];
    const double fa4 = ecc.ftime[secI][layerI][4][stripI];
    const double fa5 = ecc.ftime[secI][layerI][5][stripI];
    const double fa6 = ecc.ftime[secI][layerI][6][stripI];

    const double da0 = ecc.dtime[secI][layerI][0][stripI];
    const double da1 = ecc.dtime[secI][layerI][1][stripI];
    const double da2 = ecc.dtime[secI][layerI][2][stripI];
    const double da3 = ecc.dtime[secI][layerI][3][stripI];
    const double da4 = ecc.dtime[secI][layerI][4][stripI];
    const double da5 = ecc.dtime[secI][layerI][5][stripI];
    const double da6 = ecc.dtime[secI][layerI][6][stripI];
    const double da7 = ecc.dtime[secI][layerI][7][stripI];
    const double da8 = ecc.dtime[secI][layerI][8][stripI];

    const double fveff = ecc.fveff[secI][layerI][stripI] * 10.0;
    const double dveff = ecc.dveff[secI][layerI][stripI] * 10.0;
    const double fthr  = ecc.fthr[secI][layerI][stripI];

    const double def0 = ecc.deff[secI][layerI][0][stripI];
    const double def1 = ecc.deff[secI][layerI][1][stripI];
    const double def2 = ecc.deff[secI][layerI][2][stripI];

    const double ftres0 = ecc.ftres[secI][layerI][0][0];
    const double ftres1 = ecc.ftres[secI][layerI][1][0];
    const double ftres2 = ecc.ftres[secI][layerI][2][0];
    const double ftres3 = ecc.ftres[secI][layerI][3][0];

    const double dtres0 = ecc.dtres[secI][layerI][0][0];
    const double dtres1 = ecc.dtres[secI][layerI][1][0];
    const double dtres2 = ecc.dtres[secI][layerI][2][0];
    const double dtres3 = ecc.dtres[secI][layerI][3][0];

    double tdc_jitter = 0;
    if (ecc.jitter_cycles != 0) {
        tdc_jitter = ecc.jitter_period * static_cast<double>((0 + ecc.jitter_phase) % ecc.jitter_cycles);
    }

    for (size_t s = 0; s < nsteps; s++) {
        const double xlocal = Lpos[s].x();
        double latt = pDx2 + xlocal;
        if (view == 3 && layer > 3) latt = pDx2 - xlocal;

        const double att = A * (std::exp(-latt / B) + D * std::exp(-latt / E)) + C;
        Etota += (Edep[s] / MeV) * att;
        FTtota += latt / fveff;
        DTtota += latt / dveff;
    }

    const double base_time = ghit->getAverageTime() / ns;
    double ADC_raw         = Etota / 1000.0 / ecc.ADC_GeV_to_evio / G;
    const double FTIME_raw = base_time + FTtota / static_cast<double>(nsteps);
    const double DTIME_raw = base_time + DTtota / static_cast<double>(nsteps);

    double ADC = 0;
    if (Etota > 0) {
        double EC_npe = G4Poisson(Etota * pmtPEYld);
        if (EC_npe > 0) {
            double sigma  = std::sqrt(EC_npe) * ecc.pmtFactor;
            double EC_GeV = CLHEP::RandGauss::shoot(EC_npe, sigma)
                          / 1000.0 / ecc.ADC_GeV_to_evio / G / pmtPEYld;
            if (EC_GeV > 0) {
                ADC = EC_GeV;
                double radc = std::sqrt(ADC);
                double ftim = (fa4 == 0 || fa6 == 0) ? 0 :
                              fa0 + fa2 + std::exp(-(radc - fa3) / fa4) + 1
                              - std::exp((radc - fa5) / fa6);
                double dtim = (da4 == 0 || da6 == 0 || da7 == 0) ? 0 :
                              da0 + gtw / radc + da2 + std::exp(-(radc - da3) / da4) + 1
                              - std::exp(-(da5 - radc) / da6)
                              - std::exp(-(radc - da3 * 0.95) / da7) * std::pow(radc, da8);
                ftime_in_ns = FTIME_raw + ftim + tgo - FTOFFSET - tmf - fo;
                dtime_in_ns = DTIME_raw + dtim + tgo + tdc_jitter;
                ftime_in_ns_res = CLHEP::RandGauss::shoot(ftime_in_ns,
                                                          getTRES(ADC, ftres0, ftres2, ftres3, ftres1));
                dtime_in_ns_res = CLHEP::RandGauss::shoot(dtime_in_ns,
                                                          getTRES(ADC, dtres0, dtres2, dtres3, dtres1));
            }
        }
    }

    dtime_in_ns = ecc.outputRAW > 0 ? DTIME_raw : dtime_in_ns_res;
    ftime_in_ns = ecc.outputRAW > 0 ? FTIME_raw : ftime_in_ns_res;

    if (accountForHardwareStatus && ecc.status[secI][layerI].size() > static_cast<size_t>(stripI)) {
        switch (ecc.status[secI][layerI][stripI]) {
            case 0:
                break;
            case 1:
                ADC = ADC_raw = ftime_in_ns = 0;
                break;
            case 2:
                dtime_in_ns = 0;
                break;
            case 3:
                ADC = ADC_raw = ftime_in_ns = dtime_in_ns = 0;
                break;
            case 5:
                break;
            default:
                log->warning("Unknown ECAL status ", ecc.status[secI][layerI][stripI], " for sector ", sector,
                             ", layer ", layer, ", strip ", strip);
        }
    }

    if (ecc.outputRAW == 0 && def0 > 0 && dtime_in_ns > 0 &&
        G4UniformRand() > 1.0 / std::pow(1.0 + std::exp(-def0 * (ADC / 10.0 - def1)), def2)) {
        dtime_in_ns = 0;
    }
    if (ecc.outputRAW == 0 && ADC / 10.0 < fthr) return nullptr;

    const double fadc_time = convert_to_precision(ftime_in_ns);
    const int tdc = da1 == 0 ? 0 : static_cast<int>(dtime_in_ns / da1);

    auto digitizedData = std::make_unique<GDigitizedData>(gopts, ghit);
    digitizedData->includeVariable("hitn", static_cast<int>(hitn));
    digitizedData->includeVariable("sector", sector);
    digitizedData->includeVariable("layer", layer);
    digitizedData->includeVariable("component", strip);
    digitizedData->includeVariable("ADC_order", 0);
    digitizedData->includeVariable("ADC_ADC", ecc.outputRAW == 1 ? ADC_raw : ADC);
    digitizedData->includeVariable("ADC_time", fadc_time);
    digitizedData->includeVariable("ADC_ped", 0);
    digitizedData->includeVariable("TDC_order", 2);
    digitizedData->includeVariable("TDC_TDC", tdc);

    return digitizedData;
}
