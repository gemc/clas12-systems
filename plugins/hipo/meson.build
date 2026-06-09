clas12_plugins += [{
    'name'                : 'gstreamer_hipo_plugin',
    'sources'             : files(
        'gstreamerHIPOFactory.cc',
        'hipoSchemas.cc',
        'connection.cc',
        'event/event.cc',
        'event/eventHeader.cc',
        'event/publishDigitized.cc',
        'event/publishTrueInfo.cc',
        'event/publishGenerated.cc',
    ),
    'dependencies'        : [gemc_dep, hipo_cpp_dep],
    'include_directories' : [include_directories('.')],
}]
