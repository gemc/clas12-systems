#include "ftof.h"
#include "clas12_ccdb.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


bool FTOF_digitization::loadConstantsImpl(int runno, std::string const& variation) {
    const char* env  = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    ftc = FTOFConstants{};
    ftc.outputRAW = gopts->getScalarInt("ftof_outputRAW");
    accountForHardwareStatus = gopts->getSwitch("ftof_accountForHardwareStatus");

    ftc.pmtFactor = std::sqrt(1.0 + 1.0 / (ftc.pmtDynodeGain - 1.0));
    for (int p = 0; p < FTOFConstants::NPANEL; p++) ftc.dEMIP[p] = ftc.thick[p] * ftc.dEdxMIP;

    log->info(1, " Loading FTOF constants for run ", runno, ", variation ", variation, " from ", conn);

    auto calib = clas12ccdb::connect(conn, log);
    if (!calib) return false;
    std::vector<std::vector<double>> data;

    // attenuation length: columns [sector, panel, paddle, L, R]
    snprintf(db, sizeof(db), "/calibration/ftof/attenuation:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.attlen[isec][ilay][0].push_back(row[3]);
        ftc.attlen[isec][ilay][1].push_back(row[4]);
    }

    // effective velocity
    snprintf(db, sizeof(db), "/calibration/ftof/effective_velocity:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.veff[isec][ilay][0].push_back(row[3]);
        ftc.veff[isec][ilay][1].push_back(row[4]);
    }

    if (accountForHardwareStatus) {
        // Optional table: an empty status set is acceptable (channels default to good), so this
        // does not use clas12ccdb::loadTable, which treats an empty table as a fatal error.
        snprintf(db, sizeof(db), "/calibration/ftof/status:%d:%s", runno, variation.c_str());
        data.clear();
        calib->GetCalib(data, db);
        for (const auto& row : data) {
            int isec = static_cast<int>(row[0]) - 1;
            int ilay = static_cast<int>(row[1]) - 1;
            ftc.status[isec][ilay][0].push_back(static_cast<int>(row[3]));
            ftc.status[isec][ilay][1].push_back(static_cast<int>(row[4]));
        }
    }

    // threshold
    snprintf(db, sizeof(db), "/calibration/ftof/threshold:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.threshold[isec][ilay][0].push_back(row[3]);
        ftc.threshold[isec][ilay][1].push_back(row[4]);
    }

    // efficiency (clas12Tags copies column 3 into both sides)
    snprintf(db, sizeof(db), "/calibration/ftof/efficiency:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.efficiency[isec][ilay][0].push_back(row[3]);
        ftc.efficiency[isec][ilay][1].push_back(row[3]);
    }

    // gain balance -> counts for MIP
    snprintf(db, sizeof(db), "/calibration/ftof/gain_balance:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.countsForMIP[isec][ilay][0].push_back(row[3]);
        ftc.countsForMIP[isec][ilay][1].push_back(row[4]);
    }

    // time walk: 6 columns (5 constants each for L and R)
    snprintf(db, sizeof(db), "/calibration/ftof/time_walk:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 6; col++) ftc.twlk[isec][ilay][col].push_back(row[3 + col]);
    }

    // energy-dependent time walk: 4 columns
    snprintf(db, sizeof(db), "/calibration/ftof/time_walk_exp:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 4; col++) ftc.twlke[isec][ilay][col].push_back(row[3 + col]);
    }

    // position-dependent time walk: 2 columns
    snprintf(db, sizeof(db), "/calibration/ftof/time_walk_pos:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 2; col++) ftc.twlkp[isec][ilay][col].push_back(row[3 + col]);
    }

    // time offsets: LR, RF-paddle, paddle-to-paddle
    snprintf(db, sizeof(db), "/calibration/ftof/time_offsets:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.toff_LR[isec][ilay].push_back(row[3]);
        ftc.toff_RFpad[isec][ilay].push_back(row[4]);
        ftc.toff_P2P[isec][ilay].push_back(row[5]);
    }

    // tdc conversion factors
    snprintf(db, sizeof(db), "/calibration/ftof/tdc_conv:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.tdcconv[isec][ilay][0].push_back(row[3]);
        ftc.tdcconv[isec][ilay][1].push_back(row[4]);
    }

    // tdc jitter
    snprintf(db, sizeof(db), "/calibration/ftof/time_jitter:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    ftc.jitter_period = data[0][3];
    ftc.jitter_phase  = static_cast<int>(data[0][4]);
    ftc.jitter_cycles = static_cast<int>(data[0][5]);

    // fadc offsets
    snprintf(db, sizeof(db), "/calibration/ftof/fadc_offset:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ftc.adcoffset[isec][ilay][0].push_back(row[3]);
        ftc.adcoffset[isec][ilay][1].push_back(row[4]);
    }

    // time resolution: indexed by sector/panel/paddle
    for (int isec = 0; isec < FTOFConstants::NSECT; isec++)
        for (int ilay = 0; ilay < FTOFConstants::NPANEL; ilay++)
            ftc.tres[isec][ilay].resize(ftc.npaddles[ilay]);

    snprintf(db, sizeof(db), "/calibration/ftof/tres:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec    = static_cast<int>(row[0]) - 1;
        int ilay    = static_cast<int>(row[1]) - 1;
        int ipaddle = static_cast<int>(row[2]) - 1;
        ftc.tres[isec][ilay][ipaddle] = row[3];
    }

    // pedestals: filled with constant placeholders, as in clas12Tags
    std::fill(&ftc.pedestal[0][0][0][0],
              &ftc.pedestal[0][0][0][0] + sizeof(ftc.pedestal) / sizeof(ftc.pedestal[0][0][0][0]),
              101.0);
    std::fill(&ftc.pedestal_sigm[0][0][0][0],
              &ftc.pedestal_sigm[0][0][0][0] + sizeof(ftc.pedestal_sigm) / sizeof(ftc.pedestal_sigm[0][0][0][0]),
              2.0);

    log->info(1, " FTOF constants loaded for run ", runno, ", variation ", variation);
    return true;
}
