#pragma once

// gemc
#include "gemc/gstreamer/gstreamer.h"

// hipo plugin
#include "hipoSchemas.h"

// hipo
#include "hipo4/writer.h"
#include "hipo4/event.h"

// c++
#include <map>
#include <memory>
#include <string>
#include <vector>

/**
 * \class GStreamerHIPOFactory
 * \brief HIPO4 gstreamer output plugin for CLAS12 data.
 *
 * Writes standard CLAS12 HIPO4 banks per event:
 *   - RUN::config  (event header)
 *   - MC::True     (true hit info, accumulated across all detectors)
 *   - MC::Particle (generated particles)
 *   - MC::Event    (LUND-style event header)
 *   - Detector ADC / TDC / WF banks (one per active detector per event)
 *
 * Verbosity levels (set via `verbosity.hipo` in YAML or `-verbosity.hipo=N`):
 *   1 – file open / close messages
 *   2 – per-event bank publish details
 */
class GStreamerHIPOFactory : public GStreamer
{
public:
    explicit GStreamerHIPOFactory(const std::shared_ptr<GOptions>& g) : GStreamer(g) {
        log = std::make_shared<GLogger>(g, "GStreamerHIPOFactory", "hipo");
    }

    GStreamerHIPOFactory(const GStreamerHIPOFactory&)            = delete;
    GStreamerHIPOFactory& operator=(const GStreamerHIPOFactory&) = delete;
    GStreamerHIPOFactory(GStreamerHIPOFactory&&)                 = delete;
    GStreamerHIPOFactory& operator=(GStreamerHIPOFactory&&)      = delete;

private:
    // --- GStreamer lifecycle hooks ---
    bool openConnection() override;
    bool closeConnectionImpl() override;

    bool startRunImpl(const std::shared_ptr<GRunDataCollection>& run_data) override;

    bool startEventImpl(const std::shared_ptr<GEventDataCollection>& event_data) override;
    bool endEventImpl(const std::shared_ptr<GEventDataCollection>& event_data) override;

    bool publishEventHeaderImpl(const std::unique_ptr<GEventHeader>& gevent_header) override;

    bool publishEventTrueInfoDataImpl(
        const std::string&                       detectorName,
        const std::vector<const GTrueInfoData*>& trueInfoData) override;

    bool publishEventDigitizedDataImpl(
        const std::string&                        detectorName,
        const std::vector<const GDigitizedData*>& digitizedData) override;

    bool publishEventGeneratedParticlesImpl(
        const std::string&            bankName,
        const GGeneratedParticleBank& particles) override;

    [[nodiscard]] std::string filename() const override {
        return gstreamer_definitions.rootname + ".hipo";
    }

    // --- HIPO output resources ---
    hipo::writer                 hipoWriter;
    std::unique_ptr<HipoSchemas> schemas;
    std::unique_ptr<hipo::event> outEvent;

    // Run-level state set in startRunImpl.
    int runNumber{11};

    // Per-event MC::True accumulation buffer.
    // Rows are collected per detector in publishEventTrueInfoDataImpl
    // and assembled into a single hipo bank in endEventImpl.
    struct TrueInfoRow {
        int8_t                        detectorID{0};
        std::map<std::string, double> doubles;
    };
    std::vector<TrueInfoRow> trueInfoBuffer;

    // --- Static lookup tables defined in gstreamerHIPOFactory.cc ---

    // Detector name (lower-case, as received from GEMC) → CLAS12 detector id.
    static const std::map<std::string, int> detectorIDMap;

    // GEMC3 true-info variable name → HIPO MC::True column name.
    static const std::map<std::string, std::string> trueInfoNamesMap;

    // True-info variables that map to integer HIPO columns (all others are float).
    static const std::vector<std::string> trueInfoIntVars;

    // --- Helpers ---
    int8_t      getDetectorID(const std::string& hitType) const;
    std::string getHipoName(const std::string& varName) const;
    bool        isTrueInfoIntVar(const std::string& varName) const;
};
