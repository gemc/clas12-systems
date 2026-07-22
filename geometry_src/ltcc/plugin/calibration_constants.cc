#include "ltcc.h"
#include "clas12_ccdb.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


bool LTCC_digitization::loadConstantsImpl(int runno, std::string const& variation) {
    const char* env = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    ltccc = LTCCConstants{};

    log->info(1, " Loading LTCC constants for run ", runno, ", variation ", variation, " from ", conn);

    auto calib = clas12ccdb::connect(conn, log);
    if (!calib) return false;
    std::vector<std::vector<double>> data;

    snprintf(db, sizeof(db), "/calibration/ltcc/spe:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int sector = static_cast<int>(row[0]) - 1;
        int side = static_cast<int>(row[1]) - 1;
        int segment = static_cast<int>(row[2]) - 1;

        ltccc.speMean[sector][side][segment] = row[3];
        ltccc.speSigma[sector][side][segment] = row[4];
    }

    snprintf(db, sizeof(db), "/calibration/ltcc/time_offsets:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int sector = static_cast<int>(row[0]) - 1;
        int side = static_cast<int>(row[1]) - 1;
        int segment = static_cast<int>(row[2]) - 1;

        ltccc.timeOffset[sector][side][segment] = row[3];
        ltccc.timeRes[sector][side][segment] = row[4];
    }

    snprintf(db, sizeof(db), "/calibration/ltcc/tdc_conv:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (const auto& row : data) {
        int sector = static_cast<int>(row[0]) - 1;
        int side = static_cast<int>(row[1]) - 1;
        int segment = static_cast<int>(row[2]) - 1;

        ltccc.tdcConv[sector][side][segment] = row[3];
    }

    log->info(1, " LTCC constants loaded for run ", runno, ", variation ", variation);
    return true;
}
