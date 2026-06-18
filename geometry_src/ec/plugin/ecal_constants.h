#pragma once

#include <vector>


struct ECALConstants {
    static constexpr int NSECT  = 6;
    static constexpr int NLAYER = 9;
    static constexpr int NVIEW  = 3;

    int outputRAW = 0;

    std::vector<double> attlen[NSECT][NLAYER][10];
    std::vector<double> gain[NSECT][NLAYER];

    double jitter_period = 0;
    int    jitter_phase  = 0;
    int    jitter_cycles = 0;

    std::vector<double> dtime[NSECT][NLAYER][9];
    std::vector<double> ftime[NSECT][NLAYER][7];

    std::vector<double> fadc_offset[NSECT][NLAYER];
    std::vector<double> tmf_offset[NSECT][NLAYER];
    std::vector<double> global_time_walk[NSECT][NLAYER];

    double tdc_global_offset  = 0;
    double fadc_global_offset = 0;

    std::vector<double> dveff[NSECT][NLAYER];
    std::vector<double> fveff[NSECT][NLAYER];

    std::vector<double> deff[NSECT][NLAYER][3];
    std::vector<double> fthr[NSECT][NLAYER];

    std::vector<double> dtres[NSECT][NLAYER][4];
    std::vector<double> ftres[NSECT][NLAYER][4];

    std::vector<int> status[NSECT][NLAYER];

    double pedestal[NSECT][NLAYER][NVIEW]{};
    double pedestal_sigm[NSECT][NLAYER][NVIEW]{};

    double ADC_GeV_to_evio = 1.0 / 10000.0;
    double pmtQE           = 0.27;
    double pmtDynodeGain   = 4.0;
    double pmtDynodeK      = 0.0;
    double pmtFactor       = 0.0;

    double vpar[4]{};
};
