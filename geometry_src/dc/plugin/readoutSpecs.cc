#include "dc.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>

bool DC_digitization::defineReadoutSpecsImpl() {
	double timeWindow    = 500;                  // electronic readout time-window [ns]
	double gridStartTime = 0;                    // defines the windows grid
	auto   hitBitSet     = HitBitSet("000000");  // defines what information to be stored in the hit
	double maxStep       = 1 * CLHEP::mm;

	readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, gridStartTime, hitBitSet, maxStep, log);

	return true;
}


// DO NOT EDIT BELOW THIS LINE: defines how to create the DC_Plugin
extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
	return static_cast<GDynamicDigitization*>(new DC_digitization(g));
}
