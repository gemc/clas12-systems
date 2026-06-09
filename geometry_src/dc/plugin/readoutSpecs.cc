#include "dc.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>

bool DC_digitization::defineReadoutSpecsImpl() {
	double timeWindow    = gopts->getScalarDouble("dc_timeWindow");
	double gridStartTime = 0;
	double maxStep       = 1 * CLHEP::mm;

	readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, gridStartTime, maxStep, log);

	return true;
}


// DO NOT EDIT BELOW THIS LINE: factory entry points for the DC plugin.

extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
	return static_cast<GDynamicDigitization*>(new DC_digitization(g));
}

// Declares DC-specific options to GEMC before command-line/YAML parsing.
// GEMC probes this symbol at startup when dc appears in a gsystem list, so
// dc_timeWindow is registered in the schema and appears in --help and the
// saved configuration alongside all core options.
extern "C" GOptions* definePluginOptions() {
	// GOptions("dc") registers "dc" in the verbosity schema so users can write
	// verbosity.dc: 2  (YAML) or -verbosity.dc=2  (command line) to control
	// DC plugin log output independently of the global gdigitization verbosity.
	auto* opts = new GOptions("dc");
	opts->defineOption(
		GVariable("dc_timeWindow", 500.0, "DC electronics readout time window [ns]"),
		"Sets the drift-chamber electronics integration window. Default: 500 ns.\n"
		"Increase for late-arriving hits in high-background running conditions."
	);
	return opts;
}
