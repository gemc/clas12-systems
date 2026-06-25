#include "ftof.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


bool FTOF_digitization::defineReadoutSpecsImpl() {
    double timeWindow    = gopts->getScalarDouble("ftof_timeWindow");
    double gridStartTime = 0;
    double maxStep       = 1.0 * CLHEP::cm;

    readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, gridStartTime, maxStep, log);

    return true;
}


extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new FTOF_digitization(g));
}


extern "C" GOptions* definePluginOptions() {
    auto* opts = new GOptions("ftof");
    opts->defineOption(
        GVariable("ftof_timeWindow", 400.0, "FTOF electronics readout time window [ns]"),
        "Sets the FTOF electronics integration window. Default: 400 ns."
    );
    opts->defineOption(
        GVariable("ftof_outputRAW", 0, "Bypass FTOF threshold and efficiency rejection"),
        "When set to 1, writes FTOF ADC and timing values without threshold or efficiency rejection."
    );
    opts->defineSwitch(
        "ftof_accountForHardwareStatus",
        "Apply FTOF hardware status constants when digitizing hits"
    );
    return opts;
}
