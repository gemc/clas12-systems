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
// Exit codes follow the Meson 'exitcode' test protocol:
//   0   connected and read at least one row               -> pass
//   77  the connection could not be opened                -> SKIP (e.g. clasdb unreachable offline)
//   1   connected but the table was empty or query failed -> fail

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
        // Could not open the connection (unreachable host, offline build). Report as a skip so a
        // network-less CI run does not fail; a real connector/auth problem surfaces the same way,
        // so run this locally against a reachable clasdb to validate the connector.
        std::cerr << "SKIP: could not open CCDB connection <" << conn << ">: " << e.what() << "\n";
        return 77;
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
