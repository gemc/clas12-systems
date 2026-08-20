#include "ft_hodo.h"

// CLHEP
#include <CLHEP/Units/SystemOfUnits.h>


bool FTHODODigitization::defineReadoutSpecsImpl() {
    const double timeWindow = gopts->getRequiredScalarDouble("ft_hodo_timeWindow") * CLHEP::ns;
    readoutSpecs = std::make_shared<GReadoutSpecs>(timeWindow, 0.0, 1.0 * CLHEP::cm, log);
    return true;
}


extern "C" GDynamicDigitization* GDynamicDigitizationFactory(const std::shared_ptr<GOptions>& g) {
    return static_cast<GDynamicDigitization*>(new FTHODODigitization(g));
}
