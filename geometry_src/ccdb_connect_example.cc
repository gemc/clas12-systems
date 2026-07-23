// Minimal CCDB connect + calibration-load example, used as a Meson smoke test.
//
// It reproduces the first table read performed by the detector plugins' loadConstantsImpl (here the
// LTCC single-photoelectron table, /calibration/ltcc/spe), using only the ccdb API — no gemc
// dependency. Its purpose is to validate that the CCDB client library selected for this build (see
// the connector selection in meson/meson.build, and the MariaDB TLS patch in subprojects/ccdb.wrap)
// can actually connect to the database and return constants.
//
// Connection string: the CCDB_CONNECTION environment variable, or clasdb by default. Optional
// argv: <run> <variation> (defaults: 11 default).
//
// Exit codes: 0 on success (connected and read at least one row); non-zero on any failure — a
// connection that cannot be opened, a query error, or an empty table. The test fails hard so a
// broken CCDB client/connector (or an unreachable database) is caught rather than passed over.

#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

#include <cstdlib>
#include <exception>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    const char*       env       = std::getenv("CCDB_CONNECTION");
    const std::string conn      = env ? env : "mysql://clas12reader@clasdb.jlab.org/clas12";
    const int         run       = (argc > 1) ? std::atoi(argv[1]) : 11;
    const std::string variation = (argc > 2) ? argv[2] : "default";
    const std::string table     = "/calibration/ltcc/spe:" + std::to_string(run) + ":" + variation;

    std::cout << "ccdb_connect_example: connecting to " << conn << "\n";

    std::unique_ptr<ccdb::Calibration> calib;
    try {
        calib.reset(ccdb::CalibrationGenerator::CreateCalibration(conn));
    } catch (const std::exception& e) {
        std::cerr << "FAIL: could not open CCDB connection <" << conn << ">: " << e.what() << "\n";
        return 1;
    }

    std::vector<std::vector<double>> data;
    try {
        calib->GetCalib(data, table);
    } catch (const std::exception& e) {
        std::cerr << "FAIL: CCDB query for <" << table << "> failed: " << e.what() << "\n";
        return 1;
    }

    if (data.empty()) {
        std::cerr << "FAIL: table <" << table << "> returned no rows\n";
        return 1;
    }

    std::cout << "OK: <" << table << "> returned " << data.size() << " rows; first row:";
    for (double value : data.front()) { std::cout << ' ' << value; }
    std::cout << "\n";
    return 0;
}
