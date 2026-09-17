sro_format_test = executable('test_sro_jlab_format',
    files('jlab_sro.cc', 'tests/format_test.cc'),
    include_directories : include_directories('.'),
    dependencies : gemc_plugin_dep,
    install : false)
test('sro_jlab_format', sro_format_test, suite : ['clas12', 'sro'])

sro_gemc = find_program(gemc_prefix / 'bin' / 'gemc', required : true)
test('sro_ftcal_full_path', python_exe,
    args : [files('tests/check_ftcal_sro.py'), sro_gemc.full_path(), meson.project_build_root(),
            meson.project_source_root() / 'subprojects/ccdb/sql/ccdb.sqlite'],
    depends : clas12_plugin_targets,
    env : test_env,
    suite : ['clas12', 'sro'],
    timeout : 180)
