#include "ft_hodo.h"
#include "clas12_ccdb.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>


namespace {

template <typename T>
void set_channel(std::vector<T>& values, int component, T value) {
    if (component < 1) return;
    if (values.size() < static_cast<size_t>(component)) values.resize(component);
    values[component - 1] = value;
}

bool valid_address(const std::vector<double>& row) {
    if (row.size() < 3) return false;
    const int sector = static_cast<int>(row[0]);
    const int layer = static_cast<int>(row[1]);
    return sector >= 1 && sector <= FTHODOConstants::NSECTOR &&
           layer >= 1 && layer <= FTHODOConstants::NLAYER && row[2] >= 1;
}

} // namespace


bool FTHODODigitization::loadConstantsImpl(int runno, std::string const& variation) {
    const char* env = std::getenv("CCDB_CONNECTION");
    const std::string connection = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char table[256];

    constants = FTHODOConstants{};
    constants.ns_per_sample = 4.0 * CLHEP::ns;
    accountForHardwareStatus = gopts->getSwitch("ft_hodo_accountForHardwareStatus");

    log->info(1, " Loading FTHODO constants for run ", runno, ", variation ", variation, " from ",
              connection);

    auto calib = clas12ccdb::connect(connection, log);
    if (!calib) return false;

    std::vector<std::vector<double>> data;

    if (accountForHardwareStatus) {
        snprintf(table, sizeof(table), "/calibration/ft/fthodo/status:%d:%s", runno, variation.c_str());
        if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
        for (const auto& row : data) {
            if (!valid_address(row) || row.size() < 4) continue;
            const int sector = static_cast<int>(row[0]) - 1;
            const int layer = static_cast<int>(row[1]) - 1;
            const int component = static_cast<int>(row[2]);
            set_channel(constants.status[sector][layer], component, static_cast<int>(row[3]));
        }
    }

    snprintf(table, sizeof(table), "/calibration/ft/fthodo/noise:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
    for (const auto& row : data) {
        if (!valid_address(row) || row.size() < 8) continue;
        const int sector = static_cast<int>(row[0]) - 1;
        const int layer = static_cast<int>(row[1]) - 1;
        const int component = static_cast<int>(row[2]);
        set_channel(constants.pedestal[sector][layer], component, 101.0);
        set_channel(constants.pedestal_rms[sector][layer], component, 2.0);
        set_channel(constants.gain_pc[sector][layer], component, row[5]);
        set_channel(constants.gain_mv[sector][layer], component, row[6]);
        set_channel(constants.npe_threshold[sector][layer], component, row[7]);
    }

    snprintf(table, sizeof(table), "/calibration/ft/fthodo/charge_to_energy:%d:%s", runno,
             variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
    for (const auto& row : data) {
        if (!valid_address(row) || row.size() < 5) continue;
        const int sector = static_cast<int>(row[0]) - 1;
        const int layer = static_cast<int>(row[1]) - 1;
        const int component = static_cast<int>(row[2]);
        set_channel(constants.mips_charge[sector][layer], component, row[3]);
        set_channel(constants.mips_energy[sector][layer], component, row[4]);
    }

    snprintf(table, sizeof(table), "/calibration/ft/fthodo/time_offsets:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
    for (const auto& row : data) {
        if (!valid_address(row) || row.size() < 5) continue;
        const int sector = static_cast<int>(row[0]) - 1;
        const int layer = static_cast<int>(row[1]) - 1;
        const int component = static_cast<int>(row[2]);
        set_channel(constants.time_offset[sector][layer], component, row[3]);
        set_channel(constants.time_rms[sector][layer], component, row[4]);
    }

    log->info(1, " FTHODO constants loaded");
    return true;
}
