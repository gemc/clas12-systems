# Notice: if both static and dynamic libraries are present, the dynamic library will be used.
# Force suffix lib instead of variants like lib64.
project(
    'clas12-gemc-systems',
    'cpp',
    default_options : [
        'cpp_std=c++20',
        'default_library=static',
        'default_both_libraries=static',
        'libdir=lib',
    ],
    version : run_command('ci/clas12_plugins_version.sh', check : true).stdout().strip(),
    meson_version : '>= 1.10.1',
)

project_description = 'CLAS12 geometry systems and plugin package for GEMC digitization, magnetic fields, streamers, and calibration support.'

if get_option('buildtype') == 'debug'
    add_project_arguments('-fno-omit-frame-pointer', language : 'cpp')
    add_project_arguments('-fno-optimize-sibling-calls', language : 'cpp')
    add_project_arguments('-O2', language : 'cpp')
endif

test_env = environment()
test_env.set('PYTHONDONTWRITEBYTECODE', '1')

fs = import('fs')

# ---------------------------------------------------------------------------
# C++ plugin build infrastructure
# ---------------------------------------------------------------------------
clas12_static_libs = {}
clas12_plugins = []
clas12_plugin_targets = []

subdir('meson')   # sets up ccdb, hipo-cpp, clas12-cmag, geant4, gemc deps

# ---------------------------------------------------------------------------
# coatjava — install automatically on first configure if not present
# ---------------------------------------------------------------------------
coatjava_dir = meson.project_source_root() / 'geometry_src' / 'coatjava'
if not fs.is_dir(coatjava_dir)
    run_command(
        meson.project_source_root() / 'geometry_src' / 'install_coatjava.sh',
        '-l', check : true,
    )
endif

# ---------------------------------------------------------------------------
# Python / geometry infrastructure (pygemc)
# ---------------------------------------------------------------------------
pygemc_sub = subproject('pygemc')
venv_bin   = pygemc_sub.get_variable('venv_bin')
python_exe = import('python').find_installation(venv_bin / 'python3')

sql_db = meson.project_build_root() / 'clas12.db'

# ---------------------------------------------------------------------------
# Per-system: geometry test + C++ plugin
#
# For each system listed below meson will:
#   1. Register a test() that runs geometry_src/<sys>/<sys>.py to build
#      the geometry into the SQLite database (requires coatjava pre-installed).
#   2. subdir() into geometry_src/<sys>/plugin/ to build the C++ plugin,
#      if a meson.build exists there.
#
# Add a new detector name to the list when its directory is ready.
# ---------------------------------------------------------------------------
clas12_systems = [
    'dc',
]

foreach sys : clas12_systems
    geo_dir    = 'geometry_src' / sys
    py_script  = geo_dir / sys + '.py'
    plugin_dir = geo_dir / 'plugin'

    if fs.is_file(py_script)
        test(
            'geometry_' + sys,
            python_exe,
            args        : [py_script, '-f', 'sqlite', '-sql', sql_db],
            workdir     : meson.project_source_root() / geo_dir,
            is_parallel : false,
            env         : test_env,
            priority    : 10,
        )
    endif

    if fs.is_file(plugin_dir / 'meson.build')
        subdir(plugin_dir)
    endif
endforeach

# ---------------------------------------------------------------------------
# Build all registered shared-library plugins
# ---------------------------------------------------------------------------
foreach plugin : clas12_plugins
    plugin_target = shared_library(
        plugin['name'],
        plugin['sources'],
        install             : plugin.get('install', true),
        dependencies        : plugin.get('dependencies', []),
        include_directories : plugin.get('include_directories', []),
        link_with           : plugin.get('link_with', []),
        name_prefix         : '',
        name_suffix         : 'gplugin',
        override_options    : ['b_staticpic=true'],
    )
    clas12_plugin_targets += plugin_target
endforeach
