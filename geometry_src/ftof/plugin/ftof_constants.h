#pragma once

#include <vector>


// FTOF calibration constants, mirroring the clas12Tags `ftofConstants` struct. Arrays are indexed
// [sector][panel][side] with one std::vector entry per paddle, matching the clas12Tags CCDB layout.
struct FTOFConstants {
    static constexpr int NSECT  = 6;
    static constexpr int NPANEL = 3;   // panel 1A, 1B, 2
    static constexpr int NSIDE  = 2;   // 0 = Left PMT, 1 = Right PMT
    static constexpr int NPADDLEMAX = 62;

    int outputRAW = 0;

    // status:
    //  0 - fully functioning, 1 - noADC, 2 - noTDC, 3 - PMT dead, 5 - other
    std::vector<int> status[NSECT][NPANEL][NSIDE];

    std::vector<double> threshold[NSECT][NPANEL][NSIDE];
    std::vector<double> efficiency[NSECT][NPANEL][NSIDE];
    std::vector<double> tdcconv[NSECT][NPANEL][NSIDE];
    std::vector<double> adcoffset[NSECT][NPANEL][NSIDE];
    std::vector<double> veff[NSECT][NPANEL][NSIDE];
    std::vector<double> attlen[NSECT][NPANEL][NSIDE];
    std::vector<double> countsForMIP[NSECT][NPANEL][NSIDE];

    // time-walk corrections: 5 constants each for L and R (6 columns used)
    std::vector<double> twlk[NSECT][NPANEL][6];
    // energy-dependent time walk (4 columns)
    std::vector<double> twlke[NSECT][NPANEL][4];
    // position-dependent time walk (2 columns)
    std::vector<double> twlkp[NSECT][NPANEL][2];

    // time offsets: Left-Right, RF-paddle, paddle-to-paddle
    std::vector<double> toff_LR[NSECT][NPANEL];
    std::vector<double> toff_RFpad[NSECT][NPANEL];
    std::vector<double> toff_P2P[NSECT][NPANEL];

    // Gaussian sigma for time-resolution smearing, sized to the paddle count
    std::vector<double> tres[NSECT][NPANEL];

    // tdc jitter parameters
    double jitter_period = 0;
    int    jitter_phase  = 0;
    int    jitter_cycles = 0;

    // FADC pedestals and sigmas
    double pedestal[NSECT][NPANEL][NPADDLEMAX][NSIDE]{};
    double pedestal_sigm[NSECT][NPANEL][NPADDLEMAX][NSIDE]{};

    int    npaddles[NPANEL]{23, 62, 5};       // paddles per panel 1A, 1B, 2
    double thick[NPANEL]{5.0, 6.0, 5.0};      // paddle thickness (cm) per panel
    double dEdxMIP = 1.956;                    // nominal MIP dE/dx (MeV/g/cm^2)
    double dEMIP[NPANEL]{};                    // nominal MIP energy loss (MeV) per panel

    double pmtPEYld     = 500;                 // photoelectron yield (p.e./MeV)
    double pmtQE        = 0.27;                // PMT quantum efficiency
    double pmtDynodeGain = 4.0;               // PMT dynode gain
    double pmtDynodeK   = 0.0;                 // dynode secondary-emission factor
    double pmtFactor    = 0.0;                 // PMT statistical FWHM contribution

    // voltage signal parameters: delay, rise time, fall time, amplifier
    double vpar[4]{50.0, 10.0, 20.0, 1.0};
};
