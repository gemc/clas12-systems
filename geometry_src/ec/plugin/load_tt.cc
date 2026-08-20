#include "ecal.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


bool ECAL_digitization::loadTTImpl([[maybe_unused]] int runno, [[maybe_unused]] std::string const& variation) {
    const char* env  = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";

    log->info(1, " Loading ECAL translation table from ", conn);

    std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
    std::vector<std::vector<double>> data;

    // clas12Tags uses the fixed /daq/tt/ec:1 assignment for ECAL+PCAL.
    calib->GetCalib(data, "/daq/tt/ec:1");

    auto tt = std::make_shared<GTranslationTable>(gopts);

    for (const auto& row : data) {
        int crate   = static_cast<int>(row[0]);
        int slot    = static_cast<int>(row[1]);
        int channel = static_cast<int>(row[2]);
        int sector  = static_cast<int>(row[3]);
        int layer   = static_cast<int>(row[4]);
        int pmt     = static_cast<int>(row[5]);
        int order   = static_cast<int>(row[6]);

        tt->addGElectronicWithIdentity(
            {sector, layer, pmt, order},
            GElectronic(crate, slot, channel, GElectronic::ComparisonMode::crate));
    }

    translationTable = tt;

    log->info(1, " ECAL translation table loaded: ", data.size(), " entries");
    return true;
}
