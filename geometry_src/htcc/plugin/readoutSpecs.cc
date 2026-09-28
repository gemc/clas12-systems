#include "htcc.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


bool HTCC_digitization::defineReadoutSpecsImpl() {
    double timeWindow = gopts->getRequiredScalarDouble("htcc_timeWindow");
    double gridStartTime = 0;
    double maxStep = 1.0 * CLHEP::cm;  // clas12Tags htcc hit.pl maxStep

    readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, gridStartTime, maxStep, log);

    return true;
}


extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new HTCC_digitization(g));
}


extern "C" GOptions* definePluginOptions() {
    auto* opts = new GOptions("htcc");
    opts->defineOption(
        GVariable("htcc_timeWindow", 400.0, "HTCC electronics readout time window [ns]"),
        "Sets the HTCC electronics integration window. Default: 400 ns."
    );
    return opts;
}
