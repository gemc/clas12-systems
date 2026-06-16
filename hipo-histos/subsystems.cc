#include "subsystems.h"

#include "dc/histos.h"

#include <stdexcept>

std::unique_ptr<Subsystem> make_subsystem(const std::string &name)
{
    if (name == "dc") {
        return std::make_unique<DCSubsystem>();
    }

    throw std::runtime_error("Unsupported subsystem '" + name + "'. Currently supported: dc.");
}

std::vector<std::string> supported_subsystems()
{
    return {"dc"};
}
