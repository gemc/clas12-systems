#include "ecal.h"
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


bool ECAL_digitization::loadConstantsImpl(int runno, std::string const& variation) {
    const char* env  = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    ecc = ECALConstants{};
    ecc.outputRAW = gopts->getRequiredScalarInt("ecal_outputRAW");
    accountForHardwareStatus = gopts->getSwitch("ecal_accountForHardwareStatus");

    ecc.ADC_GeV_to_evio = 1.0 / 10000.0;
    ecc.pmtQE           = 0.27;
    ecc.pmtDynodeGain   = 4.0;
    ecc.pmtFactor       = std::sqrt(1.0 + 1.0 / (ecc.pmtDynodeGain - 1.0));

    log->info(1, " Loading ECAL constants for run ", runno, ", variation ", variation, " from ", conn);

    auto calib = clas12ccdb::connect(conn, log);
    if (!calib) return false;
    std::vector<std::vector<double>> data;

    snprintf(db, sizeof(db), "/calibration/ec/gain:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.gain[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/atten:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.attlen[isec][ilay][0].push_back(row[3]);
        ecc.attlen[isec][ilay][1].push_back(row[5]);
        ecc.attlen[isec][ilay][2].push_back(row[7]);
        ecc.attlen[isec][ilay][3].push_back(row[9]);
        ecc.attlen[isec][ilay][4].push_back(row[11]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/ftime:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 7; col++) ecc.ftime[isec][ilay][col].push_back(row[3 + col]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/dtime:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 9; col++) ecc.dtime[isec][ilay][col].push_back(row[3 + col]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/tdc_global_offset:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    ecc.tdc_global_offset = data[0][3];

    snprintf(db, sizeof(db), "/calibration/ec/fadc_global_offset:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    ecc.fadc_global_offset = data[0][3];

    snprintf(db, sizeof(db), "/calibration/ec/global_time_walk:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.global_time_walk[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/time_jitter:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    ecc.jitter_period = data[0][3];
    ecc.jitter_phase  = static_cast<int>(data[0][4]);
    ecc.jitter_cycles = static_cast<int>(data[0][5]);

    snprintf(db, sizeof(db), "/calibration/ec/fadc_offset:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.fadc_offset[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/tmf_offset:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.tmf_offset[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/fveff:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.fveff[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/dveff:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.dveff[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/deff:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.deff[isec][ilay][0].push_back(row[3]);
        ecc.deff[isec][ilay][1].push_back(row[4]);
        ecc.deff[isec][ilay][2].push_back(row[5]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/fthr:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        ecc.fthr[isec][ilay].push_back(row[3]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/ftres:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 4; col++) ecc.ftres[isec][ilay][col].push_back(row[3 + col]);
    }

    snprintf(db, sizeof(db), "/calibration/ec/dtres:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int isec = static_cast<int>(row[0]) - 1;
        int ilay = static_cast<int>(row[1]) - 1;
        for (int col = 0; col < 4; col++) ecc.dtres[isec][ilay][col].push_back(row[3 + col]);
    }

    if (accountForHardwareStatus) {
        // Optional table: an empty status set is acceptable (channels default to good), so this
        // does not use clas12ccdb::loadTable, which treats an empty table as a fatal error.
        snprintf(db, sizeof(db), "/calibration/ec/status:%d:%s", runno, variation.c_str());
        data.clear();
        calib->GetCalib(data, db);
        for (const auto& row : data) {
            int isec = static_cast<int>(row[0]) - 1;
            int ilay = static_cast<int>(row[1]) - 1;
            ecc.status[isec][ilay].push_back(static_cast<int>(row[3]));
        }
    }

    std::fill(&ecc.pedestal[0][0][0],
              &ecc.pedestal[0][0][0] + sizeof(ecc.pedestal) / sizeof(ecc.pedestal[0][0][0]),
              101.0);
    std::fill(&ecc.pedestal_sigm[0][0][0],
              &ecc.pedestal_sigm[0][0][0] + sizeof(ecc.pedestal_sigm) / sizeof(ecc.pedestal_sigm[0][0][0]),
              2.0);

    ecc.vpar[0] = 0.0;
    ecc.vpar[1] = 2.8;
    ecc.vpar[2] = 20.0;
    ecc.vpar[3] = 1.0;

    log->info(1, " ECAL constants loaded for run ", runno, ", variation ", variation);
    return true;
}
