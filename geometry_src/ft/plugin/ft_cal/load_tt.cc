#include "ft_cal.h"
#include "clas12_ccdb.h"

// c++
#include <string>
#include <vector>


bool FTCALDigitization::loadTTImpl([[maybe_unused]] int runno,
                                   [[maybe_unused]] std::string const& variation) {
    const char* env = std::getenv("CCDB_CONNECTION");
    const std::string connection = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";

    auto calib = clas12ccdb::connect(connection, log);
    if (!calib) return false;

    std::vector<std::vector<double>> data;
    if (!clas12ccdb::loadTable(calib.get(), "/daq/tt/ftcal:1", data, log)) return false;

    auto table = std::make_shared<GTranslationTable>(gopts);
    for (const auto& row : data) {
        if (row.size() < 7) continue;
        const int crate = static_cast<int>(row[0]);
        const int slot = static_cast<int>(row[1]);
        const int channel = static_cast<int>(row[2]);
        const int crystal = static_cast<int>(row[5]);
        const int ix = crystal % 22 + 1;
        const int iy = crystal / 22 + 1;

        // Geometry identifies crystals by {ih, iv}; getTTID() returns {ix, iy}.
        // Crate is the frame source; slot/channel remain available in the stored address.
        table->addGElectronicWithIdentity({ix, iy},
                                          GElectronic(crate, slot, channel,
                                                      GElectronic::ComparisonMode::crate));
    }

    translationTable = table;
    log->info(1, " FTCAL translation table loaded: ", data.size(), " entries");
    return true;
}
