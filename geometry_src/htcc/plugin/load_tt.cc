#include "htcc.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


bool HTCC_digitization::loadTTImpl(int runno, std::string const& variation) {
    const char* env = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    log->info(1, " Loading HTCC translation table for run ", runno, ", variation ", variation, " from ", conn);

    std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
    std::vector<std::vector<double>> data;

    snprintf(db, sizeof(db), "/daq/tt/htcc:%d:%s", runno, variation.c_str());
    calib->GetCalib(data, db);

    auto tt = std::make_shared<GTranslationTable>(gopts);

    // clas12Tags /daq/tt/htcc columns: crate, slot, channel, sector, half, ring, order. The GEMC3
    // hit identity order is (sector, ring, half), so key the table that way (half and ring swapped
    // relative to the raw CCDB column order) to match the digitized-hit GID.
    for (const auto& row : data) {
        int crate = static_cast<int>(row[0]);
        int slot = static_cast<int>(row[1]);
        int channel = static_cast<int>(row[2]);
        int sector = static_cast<int>(row[3]);
        int half = static_cast<int>(row[4]);
        int ring = static_cast<int>(row[5]);
        int order = row.size() > 6 ? static_cast<int>(row[6]) : 0;

        tt->addGElectronicWithIdentity(
            {sector, ring, half, order},
            GElectronic(crate, slot, channel, GElectronic::ComparisonMode::crate));
    }

    translationTable = tt;

    log->info(1, " HTCC translation table loaded: ", data.size(), " entries");
    return true;
}
