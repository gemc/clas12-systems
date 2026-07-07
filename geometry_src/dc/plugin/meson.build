clas12_plugins += [{
    'name'                : 'dc',
    'sources'             : files('readoutSpecs.cc', 'process_gtouchable.cc', 'calibration_constants.cc',
                                   'load_tt.cc', 'digitize_hit.cc', 'apply_efficiency.cc'),
    'dependencies'        : [gemc_plugin_dep, ccdb_dep],
    'include_directories' : [include_directories('.')],
}]
