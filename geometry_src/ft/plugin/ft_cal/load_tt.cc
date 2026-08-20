#include "ft_cal.h"
#include "clas12_ccdb.h"

// c++
#include <cstdlib>
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
        const int sector = static_cast<int>(row[3]);
        const int layer = static_cast<int>(row[4]);
        const int crystal = static_cast<int>(row[5]);
        const int order = static_cast<int>(row[6]);

        table->addGElectronicWithIdentity({sector, layer, crystal, order},
                                          GElectronic(crate, slot, channel,
                                                      GElectronic::ComparisonMode::crate));
    }

    translationTable = table;
    log->info(1, " FTCAL translation table loaded: ", data.size(), " entries");
    return true;
}
