#include "ft_cal.h"
#include "clas12_ccdb.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>

// c++
#include <cstdio>
#include <cstdlib>
#include <string>
#include <vector>


namespace {

bool valid_component(const std::vector<double>& row) {
    return row.size() >= 3 && row[2] >= 0 && row[2] < FTCALConstants::NCHANNEL;
}

} // namespace


bool FTCALDigitization::loadConstantsImpl(int runno, std::string const& variation) {
    using namespace CLHEP;

    const char* env = std::getenv("CCDB_CONNECTION");
    const std::string connection = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char table[256];

    constants = FTCALConstants{};
    constants.light_speed = 15.0 * cm / ns;
    accountForHardwareStatus = gopts->getSwitch("ft_cal_accountForHardwareStatus");

    log->info(1, " Loading FTCAL constants for run ", runno, ", variation ", variation, " from ", connection);

    auto calib = clas12ccdb::connect(connection, log);
    if (!calib) return false;

    std::vector<std::vector<double>> data;

    if (accountForHardwareStatus) {
        snprintf(table, sizeof(table), "/calibration/ft/ftcal/status:%d:%s", runno, variation.c_str());
        if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
        for (const auto& row : data) {
            if (!valid_component(row) || row.size() < 4) continue;
            constants.status[static_cast<int>(row[2])] = static_cast<int>(row[3]);
        }
    }

    snprintf(table, sizeof(table), "/calibration/ft/ftcal/noise:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
    for (const auto& row : data) {
        if (!valid_component(row) || row.size() < 8) continue;
        const int component = static_cast<int>(row[2]);
        constants.pedestal[component] = 101.0;
        constants.pedestal_rms[component] = 2.0;
        constants.noise[component] = row[5];
        constants.noise_rms[component] = row[6];
        constants.threshold[component] = row[7];
    }

    snprintf(table, sizeof(table), "/calibration/ft/ftcal/charge_to_energy:%d:%s", runno,
             variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
    for (const auto& row : data) {
        if (!valid_component(row) || row.size() < 8) continue;
        const int component = static_cast<int>(row[2]);
        constants.mips_charge[component] = row[3];
        constants.mips_energy[component] = row[4];
        constants.fadc_to_charge[component] = row[5];
        constants.preamp_gain[component] = row[6];
        constants.apd_gain[component] = row[7];
    }

    snprintf(table, sizeof(table), "/calibration/ft/ftcal/time_offsets:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
    for (const auto& row : data) {
        if (!valid_component(row) || row.size() < 5) continue;
        const int component = static_cast<int>(row[2]);
        constants.time_offset[component] = row[3];
        constants.time_rms[component] = row[4];
    }

    log->info(1, " FTCAL constants loaded");
    return true;
}
