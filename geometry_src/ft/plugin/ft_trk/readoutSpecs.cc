#include "ft_trk.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


bool FTTRKDigitization::defineReadoutSpecsImpl() {
    const double timeWindow = gopts->getRequiredScalarDouble("ft_trk_timeWindow") * CLHEP::ns;
    readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, 0.0, 300.0 * CLHEP::um, log);
    return true;
}


extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new FTTRKDigitization(g));
}
