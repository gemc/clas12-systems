clas12_plugins += [
    {
        # GEMC probes the gsystem name before parsing options. This registrar makes all three FT
        # digitization logger domains available while the sensitive volumes select the real plugins.
        'name'         : 'ft',
        'sources'      : files('plugin_options.cc'),
        'dependencies' : [gemc_plugin_dep],
    },
    {
        'name'                : 'ft_cal',
        'sources'             : files('ft_cal/readoutSpecs.cc', 'ft_cal/calibration_constants.cc',
                                      'ft_cal/load_tt.cc', 'ft_cal/digitize_hit.cc'),
        'dependencies'        : [gemc_plugin_dep, ccdb_dep],
        'include_directories' : [include_directories('ft_cal')],
    },
    {
        'name'                : 'ft_hodo',
        'sources'             : files('ft_hodo/readoutSpecs.cc', 'ft_hodo/calibration_constants.cc',
                                      'ft_hodo/load_tt.cc', 'ft_hodo/digitize_hit.cc'),
        'dependencies'        : [gemc_plugin_dep, ccdb_dep],
        'include_directories' : [include_directories('ft_hodo')],
    },
    {
        'name'                : 'ft_trk',
        'sources'             : files('ft_trk/readoutSpecs.cc', 'ft_trk/process_gtouchable.cc',
                                      'ft_trk/digitize_hit.cc'),
        'dependencies'        : [gemc_plugin_dep],
        'include_directories' : [include_directories('ft_trk')],
    },
]
