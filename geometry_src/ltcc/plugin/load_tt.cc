#include "ltcc.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


bool LTCC_digitization::loadTTImpl(int runno, std::string const& variation) {
    const char* env = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    log->info(1, " Loading LTCC translation table for run ", runno, ", variation ", variation, " from ", conn);

    std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
    std::vector<std::vector<double>> data;

    snprintf(db, sizeof(db), "/daq/tt/ltcc:%d:%s", runno, variation.c_str());
    calib->GetCalib(data, db);

    auto tt = std::make_shared<GTranslationTable>(gopts);

    for (const auto& row : data) {
        int crate = static_cast<int>(row[0]);
        int slot = static_cast<int>(row[1]);
        int channel = static_cast<int>(row[2]);
        int sector = static_cast<int>(row[3]);
        int side = static_cast<int>(row[4]);
        int segment = static_cast<int>(row[5]);
        int order = row.size() > 6 ? static_cast<int>(row[6]) : 0;

        tt->addGElectronicWithIdentity({sector, side, segment, order}, GElectronic(crate, slot, channel, 0));
    }

    translationTable = tt;

    log->info(1, " LTCC translation table loaded: ", data.size(), " entries");
    return true;
}
