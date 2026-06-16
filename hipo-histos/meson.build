root_config = find_program('root-config', required : false)

if root_config.found()
    root_dep = declare_dependency(
        compile_args : run_command(root_config, '--cflags', check : true).stdout().strip().split(),
        link_args    : run_command(root_config, '--libs', check : true).stdout().strip().split(),
    )

    executable(
        'hipo-histos',
        files(
            'common.cc',
            'dc/histos.cc',
            'histos_compare.cc',
            'hipo-histos.cc',
            'subsystems.cc',
        ),
        dependencies        : [hipo_cpp_dep, root_dep],
        include_directories : include_directories('.'),
        install             : true,
    )
else
    message('ROOT was not found via root-config; hipo-histos will not be built.')
endif
