#include "ltcc.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


bool LTCC_digitization::defineReadoutSpecsImpl() {
    double timeWindow = gopts->getRequiredScalarDouble("ltcc_timeWindow");
    double gridStartTime = 0;
    double maxStep = 5.0 * CLHEP::mm;

    readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, gridStartTime, maxStep, log);

    return true;
}


extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new LTCC_digitization(g));
}


extern "C" GOptions* definePluginOptions() {
    auto* opts = new GOptions("ltcc");
    opts->defineOption(
        GVariable("ltcc_timeWindow", 400.0, "LTCC electronics readout time window [ns]"),
        "Sets the LTCC electronics integration window. Default: 400 ns."
    );
    return opts;
}
