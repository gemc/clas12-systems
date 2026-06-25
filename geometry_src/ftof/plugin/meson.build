# The FTOF digitization plugin. The `ftof` geometry system declares `digitization: ftof`, so GEMC's
# startup option/verbosity probe and the runtime digitization load both resolve this `ftof.gplugin`
# by name.
clas12_plugins += [{
    'name'                : 'ftof',
    'sources'             : files('readoutSpecs.cc', 'process_gtouchable.cc', 'calibration_constants.cc',
                                   'load_tt.cc', 'digitize_hit.cc'),
    'dependencies'        : [gemc_plugin_dep, ccdb_dep],
    'include_directories' : [include_directories('.')],
}]
