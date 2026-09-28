#pragma once

// HTCC calibration constants, indexed [sector][half][ring] (all 0-based in the arrays; the CCDB
// tables are 1-based). Mirrors clas12Tags htcc_hitprocess.h htccConstants. gain, mcGain, mcSmear and
// timeShift are read per (sector, half, ring); ringShift is a per-ring time offset; tdcConv converts
// the digitized time to TDC counts. Pedestals are held constant until they are read from CCDB, exactly
// as clas12Tags does.
struct HTCCConstants {
    static constexpr int NSECT = 6;
    static constexpr int NHALF = 2;
    static constexpr int NRING = 4;

    double gain[NSECT][NHALF][NRING] = {};       // nphe -> ADC conversion
    double mcGain[NSECT][NHALF][NRING] = {};      // gain matching data yield to MC
    double mcSmear[NSECT][NHALF][NRING] = {};     // smearing matching data yield to MC
    double timeShift[NSECT][NHALF][NRING] = {};   // veff time shift
    double tdcConv[NSECT][NHALF][NRING] = {};     // TDC conversion factor
    double ringShift[NRING] = {};                 // per-ring time shift

    // FADC pedestals; constant values matching clas12Tags until read from CCDB.
    static constexpr double PEDESTAL = 101.0;
    static constexpr double PEDESTAL_SIGMA = 2.0;
};
