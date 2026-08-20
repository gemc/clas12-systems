// gemc
#include "gemc/goptions/goptions.h"


// The FT geometry contains three independently digitized subsystems. GEMC's bootstrap scan probes the
// gsystem name (`ft.gplugin`) before parsing YAML, so this options-only plugin registers every logger domain.
// Geometry loading later discovers and instantiates ft_cal.gplugin, ft_hodo.gplugin, and ft_trk.gplugin from
// the sensitive volumes' digitization fields.
extern "C" GOptions* definePluginOptions() {
    auto* options = new GOptions("ft_cal");
    options->defineOption(
        GVariable("ft_cal_timeWindow", 400.0, "FTCAL electronics readout time window [ns]"),
        "Sets the FTCAL electronics integration window. Default: 400 ns.");
    options->defineSwitch(
        "ft_cal_accountForHardwareStatus", "Apply FTCAL hardware status constants when digitizing hits");

    GOptions hodoOptions("ft_hodo");
    hodoOptions.defineOption(
        GVariable("ft_hodo_timeWindow", 400.0, "FTHODO electronics readout time window [ns]"),
        "Sets the FTHODO electronics integration window. Default: 400 ns.");
    hodoOptions.defineSwitch(
        "ft_hodo_accountForHardwareStatus", "Apply FTHODO hardware status constants when digitizing hits");
    *options += hodoOptions;

    GOptions trackerOptions("ft_trk");
    trackerOptions.defineOption(
        GVariable("ft_trk_timeWindow", 132.0, "FTTRK electronics readout time window [ns]"),
        "Sets the FTTRK electronics integration window. Default: 132 ns.");
    *options += trackerOptions;
    return options;
}
