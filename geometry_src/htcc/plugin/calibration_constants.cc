#include "htcc.h"
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


bool HTCC_digitization::loadConstantsImpl(int runno, std::string const& variation) {
    const char* env = std::getenv("CCDB_CONNECTION");
    std::string conn = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    char db[256];

    htccc = HTCCConstants{};

    log->info(1, " Loading HTCC constants for run ", runno, ", variation ", variation, " from ", conn);

    auto calib = clas12ccdb::connect(conn, log);
    if (!calib) return false;
    std::vector<std::vector<double>> data;

    // gain, mc_gain, mc_smear, time and tdc_conv are all keyed by (sector, half, ring) in columns
    // 0..2, with the value in column 3 (clas12Tags htcc_hitprocess initializeHTCCConstants).
    auto loadPerRing =
        [&](const char* table,
            double (&arr)[HTCCConstants::NSECT][HTCCConstants::NHALF][HTCCConstants::NRING]) -> bool {
        if (!clas12ccdb::loadTable(calib.get(), table, data, log)) return false;
        for (const auto& row : data) {
            int s = static_cast<int>(row[0]) - 1;
            int h = static_cast<int>(row[1]) - 1;
            int r = static_cast<int>(row[2]) - 1;
            if (s < 0 || s >= HTCCConstants::NSECT || h < 0 || h >= HTCCConstants::NHALF ||
                r < 0 || r >= HTCCConstants::NRING)
                continue;
            arr[s][h][r] = row[3];
        }
        return true;
    };

    snprintf(db, sizeof(db), "/calibration/htcc/gain:%d:%s", runno, variation.c_str());
    if (!loadPerRing(db, htccc.gain)) return false;

    snprintf(db, sizeof(db), "/calibration/htcc/mc_gain:%d:%s", runno, variation.c_str());
    if (!loadPerRing(db, htccc.mcGain)) return false;

    snprintf(db, sizeof(db), "/calibration/htcc/mc_smear:%d:%s", runno, variation.c_str());
    if (!loadPerRing(db, htccc.mcSmear)) return false;

    snprintf(db, sizeof(db), "/calibration/htcc/time:%d:%s", runno, variation.c_str());
    if (!loadPerRing(db, htccc.timeShift)) return false;

    snprintf(db, sizeof(db), "/calibration/htcc/tdc_conv:%d:%s", runno, variation.c_str());
    if (!loadPerRing(db, htccc.tdcConv)) return false;

    // ring_time is a per-ring shift. clas12Tags reads the value column (col 3) row by row into a
    // per-ring vector, so the first NRING rows are rings 1..NRING in order.
    snprintf(db, sizeof(db), "/calibration/htcc/ring_time:%d:%s", runno, variation.c_str());
    if (!clas12ccdb::loadTable(calib.get(), db, data, log)) return false;
    for (int ringRow = 0; ringRow < HTCCConstants::NRING && ringRow < static_cast<int>(data.size());
         ringRow++) {
        htccc.ringShift[ringRow] = data[ringRow][3];
    }

    log->info(1, " HTCC constants loaded for run ", runno, ", variation ", variation);
    return true;
}
