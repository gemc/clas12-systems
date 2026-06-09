// hipo plugin
#include "gstreamerHIPOFactory.h"

// gemc
#include "gemc/gstreamer/gstreamerConventions.h"


// ---------------------------------------------------------------------------
// Plugin entry points
// ---------------------------------------------------------------------------

extern "C" GStreamer* GStreamerFactory(const std::shared_ptr<GOptions>& g) {
    return new GStreamerHIPOFactory(g);
}

// Registers the "hipo" verbosity domain so users can write:
//   verbosity.hipo: 1   (file open/close)
//   verbosity.hipo: 2   (per-event bank details)
extern "C" GOptions* definePluginOptions() {
    return new GOptions("hipo");
}


// ---------------------------------------------------------------------------
// Static lookup tables
// ---------------------------------------------------------------------------

const std::map<std::string, int> GStreamerHIPOFactory::detectorIDMap = {
    {"bmt",     1},
    {"bst",     2},
    {"cnd",     3},
    {"ctof",    4},
    {"dc",      6},
    {"ecal",    7},
    {"fmt",     8},
    {"ft_cal",  10},
    {"ft_hodo", 11},
    {"ft_trk",  13},
    {"ftof",    12},
    {"htcc",    15},
    {"ltcc",    16},
    {"rich",    18},
    {"rtpc",    19},
    {"band",    21},
    {"urwt",    23},
    {"atof",    24},
    {"ahdc",    25},
    {"recoil",  26},
    {"mucal",   28},
    {"muvt",    29},
    {"murt",    30},
    {"murh",    31},
    {"flux",   100},
};

// GEMC3 variable name  →  HIPO MC::True column name
const std::map<std::string, std::string> GStreamerHIPOFactory::trueInfoNamesMap = {
    {"pid",              "pid"},
    {"mpid",             "mpid"},
    {"tid",              "tid"},
    {"mtid",             "mtid"},
    {"otid",             "otid"},
    {"trackE",           "trackE"},
    {"totalEDeposited",  "totEdep"},
    {"avgx",             "avgX"},
    {"avgy",             "avgY"},
    {"avgz",             "avgZ"},
    {"avglx",            "avgLx"},
    {"avgly",            "avgLy"},
    {"avglz",            "avgLz"},
    {"px",               "px"},
    {"py",               "py"},
    {"pz",               "pz"},
    {"vx",               "vx"},
    {"vy",               "vy"},
    {"vz",               "vz"},
    {"mvx",              "mvx"},
    {"mvy",              "mvy"},
    {"mvz",              "mvz"},
    {"avgTime",          "avgT"},
    {"nsteps",           "nsteps"},
    {"procID",           "procID"},
    {"hitn",             "hitn"},
};

// These MC::True columns are written with putInt (the rest with putFloat).
const std::vector<std::string> GStreamerHIPOFactory::trueInfoIntVars = {
    "pid", "mpid", "tid", "mtid", "otid", "nsteps", "procID", "hitn",
};


// ---------------------------------------------------------------------------
// Helper methods
// ---------------------------------------------------------------------------

int8_t GStreamerHIPOFactory::getDetectorID(const std::string& hitType) const {
    auto it = detectorIDMap.find(hitType);
    if (it != detectorIDMap.end()) return static_cast<int8_t>(it->second);
    log->info(2, FUNCTION_NAME, "no detector id for '", hitType, "', using 0");
    return 0;
}

std::string GStreamerHIPOFactory::getHipoName(const std::string& varName) const {
    auto it = trueInfoNamesMap.find(varName);
    return (it != trueInfoNamesMap.end()) ? it->second : std::string{};
}

bool GStreamerHIPOFactory::isTrueInfoIntVar(const std::string& hipoName) const {
    for (const auto& name : trueInfoIntVars) {
        if (name == hipoName) return true;
    }
    return false;
}
