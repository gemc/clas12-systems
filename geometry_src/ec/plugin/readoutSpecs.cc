#include "ecal.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


bool ECAL_digitization::defineReadoutSpecsImpl() {
    double timeWindow    = gopts->getScalarDouble("ecal_timeWindow");
    double gridStartTime = 0;
    double maxStep       = 5.0 * CLHEP::mm;

    readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, gridStartTime, maxStep, log);

    return true;
}


extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new ECAL_digitization(g));
}


extern "C" GOptions* definePluginOptions() {
    auto* opts = new GOptions("ecal");
    opts->defineOption(
        GVariable("ecal_timeWindow", 400.0, "ECAL electronics readout time window [ns]"),
        "Sets the ECAL electronics integration window. Default: 400 ns."
    );
    opts->defineOption(
        GVariable("ecal_outputRAW", 0, "Bypass ECAL calibration, resolution, and efficiency"),
        "When set to 1, writes raw ECAL ADC and timing values without threshold, efficiency, or smearing."
    );
    opts->defineSwitch(
        "ecal_accountForHardwareStatus",
        "Apply ECAL hardware status constants when digitizing hits"
    );
    return opts;
}
