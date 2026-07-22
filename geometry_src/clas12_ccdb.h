#pragma once

/**
 * \file clas12_ccdb.h
 * \brief Shared CCDB helpers for the CLAS12 detector digitization plugins.
 *
 * Every detector's loadConstantsImpl opens a CCDB connection and reads a series of tables into a
 * `std::vector<std::vector<double>>` with `ccdb::Calibration::GetCalib`. Two failure modes are
 * handled here so plugins can fail loudly instead of crashing or digitizing to nothing:
 *
 * - The connection fails. ccdb throws `std::logic_error` from `CreateCalibration` (a wrong
 *   `CCDB_CONNECTION`, an unreachable host, or a client library that cannot authenticate to the
 *   server). `connect` catches it, logs, and returns nullptr instead of letting it reach
 *   std::terminate.
 * - A mandatory table comes back empty (a wrong database, or a run/variation with no entry). Left
 *   unchecked this is silent: constants keep their defaults and digitization drops every hit — or
 *   worse, a `data[0][...]` access on the empty vector is undefined behavior. `loadTable` fetches the
 *   table and reports whether it returned any rows.
 *
 * Callers should `return false` from loadConstantsImpl on either failure; the event dispenser turns
 * that into a fatal error with a clear message.
 */

// CCDB
#include <CCDB/Calibration.h>
#include <CCDB/CalibrationGenerator.h>

// gemc
#include "gemc/glogging/glogger.h"

// c++
#include <exception>
#include <memory>
#include <string>
#include <vector>

namespace clas12ccdb {

/**
 * \brief Opens a CCDB connection, catching the exception ccdb throws on failure.
 *
 * `ccdb::CalibrationGenerator::CreateCalibration` throws `std::logic_error` when it cannot connect
 * (bad connection string, unreachable host, or a MySQL client library that cannot authenticate to
 * the server). This catches that, logs an error, and returns nullptr so the plugin can
 * `return false` from loadConstantsImpl rather than letting the exception terminate the process.
 *
 * \param conn CCDB connection string (e.g. "mysql://clas12reader@clasdb.jlab.org/clas12").
 * \param log  Logger used to report a failed connection.
 * \return A calibration handle, or nullptr if the connection could not be opened.
 */
inline std::unique_ptr<ccdb::Calibration> connect(const std::string& conn,
                                                  const std::shared_ptr<GLogger>& log) {
    try {
        return std::unique_ptr<ccdb::Calibration>(
            ccdb::CalibrationGenerator::CreateCalibration(conn));
    } catch (const std::exception& e) {
        log->warning("could not open CCDB connection <", conn, ">: ", e.what(),
                     " — check CCDB_CONNECTION.");
        return nullptr;
    }
}

/**
 * \brief Fetches one CCDB table into \p data and reports whether it returned any rows.
 *
 * Clears \p data, calls `GetCalib(data, table)`, and on an empty result logs a warning naming the
 * table and returns \c false. Callers loading a mandatory table should `return false` from
 * loadConstantsImpl so the run aborts with a clear message rather than digitizing to nothing.
 *
 * \param calib  CCDB calibration handle.
 * \param table  Fully-formed CCDB table path (e.g. "/calibration/ltcc/spe:11:default").
 * \param data   Destination row/column matrix; cleared before the fetch.
 * \param log    Logger used to report an empty table.
 * \return \c true if the table returned at least one row, \c false otherwise.
 */
inline bool loadTable(ccdb::Calibration* calib,
                      const std::string& table,
                      std::vector<std::vector<double>>& data,
                      const std::shared_ptr<GLogger>& log) {
    data.clear();
    try {
        calib->GetCalib(data, table);
    } catch (const std::exception& e) {
        log->warning("CCDB query for table <", table, "> failed: ", e.what(),
                     " — check CCDB_CONNECTION.");
        return false;
    }
    if (data.empty()) {
        log->warning("CCDB table <", table, "> returned no rows — digitized output would be empty. "
                     "Check CCDB_CONNECTION.");
        return false;
    }
    return true;
}

}  // namespace clas12ccdb
