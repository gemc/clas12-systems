#include "subsystems.h"

#include "dc/histos.h"
#include "ec/histos.h"

#include <stdexcept>

std::unique_ptr<Subsystem> make_subsystem(const std::string &name)
{
    if (name == "dc") {
        return std::make_unique<DCSubsystem>();
    }
    if (name == "ec") {
        return std::make_unique<ECSubsystem>();
    }

    throw std::runtime_error("Unsupported subsystem '" + name + "'. Currently supported: dc, ec.");
}

std::vector<std::string> supported_subsystems()
{
    return {"dc", "ec"};
}
