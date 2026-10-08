sro_format_test = executable('test_sro_jlab_format',
    files('jlab_sro.cc', 'tests/format_test.cc'),
    include_directories : include_directories('.'),
    dependencies : gemc_plugin_dep,
    install : false)
test('sro_jlab_format', sro_format_test, suite : ['clas12', 'sro'])

test('sro_ftcal_full_path', python_exe,
    args : [files('tests/check_ftcal_sro.py'), gemc_test_path, meson.project_build_root(),
            meson.project_source_root() / 'subprojects/ccdb/sql/ccdb.sqlite'],
    depends : gemc_test_depends,
    env : test_env,
    suite : ['clas12', 'sro'],
    timeout : 180)
