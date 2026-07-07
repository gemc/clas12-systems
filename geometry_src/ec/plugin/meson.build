# The ECAL digitization plugin is shared by the EC and PCAL geometry systems. Each system's YAML declares
# `digitization: ecal` so GEMC's startup option/verbosity probe loads this plugin (the probe is keyed by the
# gsystem name plus the optional digitization name), and the runtime digitization load finds it by the gvolume
# digitization name. A single `ecal.gplugin` therefore serves both systems.
clas12_plugins += [{
    'name'                : 'ecal',
    'sources'             : files('readoutSpecs.cc', 'process_gtouchable.cc', 'calibration_constants.cc',
                                   'load_tt.cc', 'digitize_hit.cc', 'apply_thresholds.cc',
                                   'apply_efficiency.cc'),
    'dependencies'        : [gemc_plugin_dep, ccdb_dep],
    'include_directories' : [include_directories('.')],
}]
