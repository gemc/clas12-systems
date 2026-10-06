sro_format_test = executable('test_sro_jlab_format',
    files('jlab_sro.cc', 'tests/format_test.cc'),
    include_directories : include_directories('.'),
    dependencies : gemc_plugin_dep,
    install : false)
test('sro_jlab_format', sro_format_test, suite : ['clas12', 'sro'])

# gemc_exe is resolved in meson/meson.build: an installed binary, or the subproject build target when
# GEMC is built from source.
#
# gemc infers its runtime root (lib/, examples/, ...) from the executable's location. The subproject
# build-tree binary (build/subprojects/gemc/bin/gemc) has no such layout beside it and aborts with
# "Cannot locate directory <lib>". So when GEMC is built here, run the copy installed into this
# build's prefix instead — it carries the proper layout. This requires `meson install` to have run
# before `meson test` (ci/build.sh installs first; run `meson install -C build` before testing
# locally). The gemc target stays in `depends` so the binary is built.
if gemc_is_subproject
    sro_gemc_path = get_option('prefix') / 'bin' / 'gemc'
    sro_gemc_depends = clas12_plugin_targets + [gemc_exe]
else
    sro_gemc_path = gemc_exe.full_path()
    sro_gemc_depends = clas12_plugin_targets
endif
test('sro_ftcal_full_path', python_exe,
    args : [files('tests/check_ftcal_sro.py'), sro_gemc_path, meson.project_build_root(),
            meson.project_source_root() / 'subprojects/ccdb/sql/ccdb.sqlite'],
    depends : sro_gemc_depends,
    env : test_env,
    suite : ['clas12', 'sro'],
    timeout : 180)
