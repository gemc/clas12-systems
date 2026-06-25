#include "ftof.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


bool FTOF_digitization::loadTTImpl([[maybe_unused]] int runno, [[maybe_unused]] std::string const& variation) {
    const char* env  = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";

    log->info(1, " Loading FTOF translation table from ", conn);

    std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
    std::vector<std::vector<double>> data;

    // clas12Tags uses the fixed /daq/tt/ftof:1 assignment.
    calib->GetCalib(data, "/daq/tt/ftof:1");

    auto tt = std::make_shared<GTranslationTable>(gopts);

    for (const auto& row : data) {
        int crate   = static_cast<int>(row[0]);
        int slot    = static_cast<int>(row[1]);
        int channel = static_cast<int>(row[2]);
        int sector  = static_cast<int>(row[3]);
        int panel   = static_cast<int>(row[4]);
        int paddle  = static_cast<int>(row[5]);
        int pmt     = static_cast<int>(row[6]);

        tt->addGElectronicWithIdentity({sector, panel, paddle, pmt}, GElectronic(crate, slot, channel, 0));
    }

    translationTable = tt;

    log->info(1, " FTOF translation table loaded: ", data.size(), " entries");
    return true;
}
