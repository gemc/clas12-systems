// dc plugin
#include "dc.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/Model/Assignment.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


// Ported from dc_HitProcess::initializeDCConstants in clas12Tags.
// Reads all DC calibration tables from CCDB and populates the dcc member.
bool DC_digitization::loadConstantsImpl(int runno, std::string const& variation) {
    const char* env    = std::getenv("CCDB_CONNECTION");
    std::string conn   = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char        db[256];

    log->info(1, " Loading DC constants for run ", runno, ", variation ", variation, " from ", conn);

    std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
    std::vector<std::vector<double>>   data;

    // -- efficiency parameters
    snprintf(db, sizeof(db), "/calibration/dc/signal_generation/inefficiency:%d:%s",
             runno, variation.c_str());
    calib->GetCalib(data, db);
    for (const auto& row : data) {
        int sec = static_cast<int>(row[0]) - 1;
        int sl  = static_cast<int>(row[1]) - 1;
        dcc.iScale[sec][sl] = row[3];
        dcc.P1[sec][sl]     = row[4];
        dcc.P2[sec][sl]     = row[5];
        dcc.P3[sec][sl]     = row[6];
        dcc.P4[sec][sl]     = row[7];
    }

    // -- smearing parameters
    snprintf(db, sizeof(db), "/calibration/dc/signal_generation/doca_smearing:%d:%s",
             runno, variation.c_str());
    data.clear();
    calib->GetCalib(data, db);
    for (const auto& row : data) {
        int sec = static_cast<int>(row[0]) - 1;
        int sl  = static_cast<int>(row[1]) - 1;
        dcc.smearP0[sec][sl] = row[3];
        dcc.smearP1[sec][sl] = row[4];
        dcc.smearP2[sec][sl] = row[5];
        dcc.smearP3[sec][sl] = row[6];
        dcc.smearP4[sec][sl] = row[7];
    }

    // -- pressure correction for t2d: (current - reference) pressure
    snprintf(db, sizeof(db), "/calibration/dc/v2/ref_pressure:%d:%s", runno, variation.c_str());
    data.clear();
    calib->GetCalib(data, db);
    double ref_pressure = data[0][3];

    snprintf(db, sizeof(db), "/hall/weather/pressure:%d:%s", runno, variation.c_str());
    data.clear();
    calib->GetCalib(data, db);
    double dpressure = data[3][3] - ref_pressure;

    // -- time-to-distance parameters (pressure-corrected quadratic expansion)
    snprintf(db, sizeof(db), "/calibration/dc/v2/t2d_pressure:%d:%s", runno, variation.c_str());
    data.clear();
    calib->GetCalib(data, db);
    for (const auto& row : data) {
        int    sec = static_cast<int>(row[0]) - 1;
        int    sl  = static_cast<int>(row[1]) - 1;
        double dp  = dpressure;
        double dp2 = dp * dp;
        dcc.v0[sec][sl]                       = row[3]  + row[4]*dp  + row[5]*dp2;
        dcc.vmid[sec][sl]                     = row[6]  + row[7]*dp  + row[8]*dp2;
        dcc.tmaxsuperlayer[sec][sl]           = row[9]  + row[10]*dp + row[11]*dp2;
        dcc.distbeta[sec][sl]                 = row[12] + row[13]*dp + row[14]*dp2;
        dcc.delta_bfield_coefficient[sec][sl] = row[15] + row[16]*dp + row[17]*dp2;
        dcc.deltatime_bfield_par1[sec][sl]    = row[18] + row[19]*dp + row[20]*dp2;
        dcc.deltatime_bfield_par2[sec][sl]    = row[21] + row[22]*dp + row[23]*dp2;
        dcc.deltatime_bfield_par3[sec][sl]    = row[24] + row[25]*dp + row[26]*dp2;
        dcc.deltatime_bfield_par4[sec][sl]    = row[27] + row[28]*dp + row[29]*dp2;
        dcc.R[sec][sl]                        = row[30] + row[31]*dp;
    }

    // -- wire readout side (hardcoded — matches CLAS12 reconstruction)
    for (int s = 0; s < 6; s++) {
        dcc.stbloc[s][0] =  1;
        dcc.stbloc[s][1] = -1;
        dcc.stbloc[s][4] =  1;
        dcc.stbloc[s][5] =  1;
    }
    for (int sl = 2; sl < 4; sl++) {
        dcc.stbloc[2][sl] =  1;
        dcc.stbloc[3][sl] =  1;
        dcc.stbloc[4][sl] =  1;
        dcc.stbloc[0][sl] = -1;
        dcc.stbloc[1][sl] = -1;
        dcc.stbloc[5][sl] = -1;
    }

    // -- T0 corrections
    snprintf(db, sizeof(db), "/calibration/dc/v2/t0:%d:%s", runno, variation.c_str());
    data.clear();
    calib->GetCalib(data, db);
    for (const auto& row : data) {
        int sec   = static_cast<int>(row[0]) - 1;
        int sl    = static_cast<int>(row[1]) - 1;
        int slot  = static_cast<int>(row[2]) - 1;
        int cable = static_cast<int>(row[3]) - 1;
        dcc.T0Correction[sec][sl][slot][cable] = row[4];
    }

    // -- TDC jitter
    snprintf(db, sizeof(db), "/calibration/dc/time_jitter:%d:%s", runno, variation.c_str());
    data.clear();
    calib->GetCalib(data, db);
    dcc.jitter_period = data[0][3];
    dcc.jitter_phase  = static_cast<int>(data[0][4]);
    dcc.jitter_cycles = static_cast<int>(data[0][5]);

    // -- DC core geometry: cell size per superlayer, used for wire position and doca
    snprintf(db, sizeof(db), "/geometry/dc/superlayer:%d:%s", runno, variation.c_str());
    std::unique_ptr<ccdb::Assignment> dcCore(calib->GetAssignment(db));
    for (size_t row = 0; row < dcCore->GetRowsCount(); row++) {
        dcc.dLayer[row] = dcCore->GetValueDouble(row, 6);
    }
    for (int sl = 0; sl < 6; sl++) {
        dcc.dmaxsuperlayer[sl] = 2.0 * dcc.dLayer[sl];
    }

    // -- mini-stagger offsets: layers 1,3,5 (0-indexed 0,2,4) shift +0.300 mm;
    //    layers 2,4,6 (0-indexed 1,3,5) shift -0.300 mm
    for (int l = 0; l < 6; l++) {
        dcc.miniStagger[l] = (l % 2 == 0) ? 0.300 * CLHEP::mm : -0.300 * CLHEP::mm;
    }

    log->info(1, " DC constants loaded for run ", runno, ", variation ", variation);

    return true;
}
