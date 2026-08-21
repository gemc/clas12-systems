#include "subsystems.h"

#include "dc/histos.h"
#include "ec/histos.h"
#include "ft/histos.h"
#include "ftof/histos.h"
#include "ltcc/histos.h"
#include "pcal/histos.h"

#include <stdexcept>

std::unique_ptr<Subsystem> make_subsystem(const std::string &name)
{
    if (name == "dc") {
        return std::make_unique<DCSubsystem>();
    }
    if (name == "ec") {
        return std::make_unique<ECSubsystem>();
    }
    if (name == "ft") {
        return std::make_unique<FTSubsystem>();
    }
    if (name == "ftof") {
        return std::make_unique<FTOFSubsystem>();
    }
    if (name == "ltcc") {
        return std::make_unique<LTCCSubsystem>();
    }
    if (name == "pcal") {
        return std::make_unique<PCALSubsystem>();
    }

    throw std::runtime_error("Unsupported subsystem '" + name +
                             "'. Currently supported: dc, ec, ft, ftof, ltcc, pcal.");
}

std::vector<std::string> supported_subsystems()
{
    return {"dc", "ec", "ft", "ftof", "ltcc", "pcal"};
}
