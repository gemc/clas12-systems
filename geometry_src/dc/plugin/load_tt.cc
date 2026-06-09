// dc plugin
#include "dc.h"

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// c++
#include <cstdio>
#include <cstdlib>
#include <memory>
#include <string>
#include <vector>


// Ported from dc_HitProcess::initializeDCConstants (translation table block) in clas12Tags.
// The /daq/tt/dc table maps (crate, slot, channel) hardware addresses to
// (sector, superlayer, layer, wire) detector identities.
bool DC_digitization::loadTTImpl(int runno, std::string const& variation) {
    const char* env  = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    log->info(1, " Loading DC translation table for run ", runno, ", variation ", variation, " from ", conn);

    std::unique_ptr<ccdb::Calibration> calib(ccdb::CalibrationGenerator::CreateCalibration(conn));
    std::vector<std::vector<double>>   data;

    snprintf(db, sizeof(db), "/daq/tt/dc:%d:%s", runno, variation.c_str());
    calib->GetCalib(data, db);

    auto tt = std::make_shared<GTranslationTable>(gopts);

    for (const auto& row : data) {
        int crate  = static_cast<int>(row[0]);
        int slot   = static_cast<int>(row[1]);
        int chan   = static_cast<int>(row[2]);
        int sector = static_cast<int>(row[3]);
        int sl     = static_cast<int>(row[4]);
        int layer  = static_cast<int>(row[5]);
        int wire   = static_cast<int>(row[6]);
        // mode 2: full crate/slot/channel resolution
        tt->addGElectronicWithIdentity({sector, sl, layer, wire}, GElectronic(crate, slot, chan, 2));
    }

    translationTable = tt;

    log->info(1, " DC translation table loaded: ", data.size(), " entries");
    return true;
}
