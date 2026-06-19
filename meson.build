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

project_description = 'CLAS12 geometry systems and plugins for GEMC'

if get_option('buildtype') == 'debug'
    add_project_arguments('-fno-omit-frame-pointer', language : 'cpp')
    add_project_arguments('-fno-optimize-sibling-calls', language : 'cpp')
    add_project_arguments('-O2', language : 'cpp')
endif

test_env = environment()
test_env.set('PYTHONDONTWRITEBYTECODE', '1')
test_env.prepend('PYTHONPATH', meson.project_source_root() / 'geometry_src')

fs = import('fs')
javac = find_program(
    '/opt/homebrew/opt/java/bin/javac',
    '/usr/local/opt/java/bin/javac',
    'javac',
    required : true,
)

# ---------------------------------------------------------------------------
# C++ plugin build infrastructure
#
# System plugin meson.build files append dictionaries to clas12_plugins:
#
#   clas12_plugins += [{
#       'name' : 'dc',
#       'sources' : files('dc.cc'),
#       'dependencies' : [gemc_dep],
#   }]
#
# The top-level loop below is the only place that turns those registry entries
# into installed GEMC shared-library plugins.
# ---------------------------------------------------------------------------
clas12_static_libs = {}
clas12_plugins = []
clas12_plugin_targets = []

subdir('meson')   # sets up ccdb, hipo-cpp, clas12-cmag, geant4, gemc deps

clas12_sanitize = get_option('clas12_sanitize')
if clas12_sanitize != 'none'
    clas12_sanitize_arg = '-fsanitize=' + clas12_sanitize
    add_project_arguments(
        clas12_sanitize_arg,
        '-fno-omit-frame-pointer',
        language : 'cpp',
    )
    add_project_link_arguments(clas12_sanitize_arg, language : 'cpp')
endif

# coatjava — install automatically on first configure if not present.
# CI installs Java, git-lfs, and jq before this point.
coatjava_dir = meson.project_source_root() / 'geometry_src' / 'coatjava'
if not fs.is_dir(coatjava_dir)
    run_command(
        meson.project_source_root() / 'geometry_src' / 'install_coatjava.sh',
        '-l', check : true,
    )
endif

coatjava_classpath = ':'.join([
    coatjava_dir / 'lib' / 'clas' / '*',
    coatjava_dir / 'lib' / 'services' / '*',
    coatjava_dir / 'lib' / 'utils' / '*',
])

coatjava_factory_classes = custom_target(
    'coatjava_factory_classes',
    input   : 'geometry_src/coatjava_factories/CoatjavaFactory.java',
    output  : ['CoatjavaFactory.class', 'CoatjavaFactory$Options.class'],
    build_by_default : true,
    command : [
        javac,
        '-cp', coatjava_classpath,
        '-d', '@OUTDIR@',
        '@INPUT@',
    ],
)
test_env.set('COATJAVA_FACTORY_CLASSES', meson.current_build_dir())

# Python / geometry infrastructure (pygemc)
pygemc_sub = subproject('pygemc')
venv_bin   = pygemc_sub.get_variable('venv_bin')
python_exe = import('python').find_installation(venv_bin / 'python3')

# Register geometry_src/ in the venv via a .pth file so every detector script
# can import clas12_common without per-detector sys.path boilerplate.
# Python processes .pth files at interpreter startup for any use of this venv.
run_command(
    python_exe, '-c',
    'import sys, sysconfig, pathlib; '
    + 'pathlib.Path(sysconfig.get_path("purelib"), "clas12_systems.pth").write_text(sys.argv[1])',
    meson.project_source_root() / 'geometry_src',
    check : true,
)

sql_db = meson.project_build_root() / 'clas12.db'

# ---------------------------------------------------------------------------
# Per-system: geometry test + C++ plugin registry
#
# For each system listed below meson will:
#   1. Register a test() that runs geometry_src/<sys>/<sys>.py to build
#      the geometry into the SQLite database (requires coatjava pre-installed).
#   2. subdir() into geometry_src/<sys>/plugin/ so the system can register
#      any C++ plugin shared libraries in clas12_plugins.
#
# Add a new detector name to the list when its directory is ready.
# ---------------------------------------------------------------------------
clas12_systems = [
    'dc',
    'ec',
]

foreach sys : clas12_systems
    geo_dir    = 'geometry_src' / sys
    py_script  = geo_dir / sys + '.py'
    py_script_name = sys + '.py'
    plugin_dir = geo_dir / 'plugin'

    if fs.is_file(py_script)
        test(
            'geometry_' + sys,
            python_exe,
            args        : [py_script_name, '-f', 'sqlite', '-sql', sql_db],
            workdir     : meson.project_source_root() / geo_dir,
            is_parallel : false,
            env         : test_env,
            depends     : coatjava_factory_classes,
            priority    : 10,
            suite       : 'clas12',
            timeout     : 180,
        )
    endif

    if fs.is_file(plugin_dir / 'meson.build')
        subdir(plugin_dir)
    endif
endforeach

# ---------------------------------------------------------------------------
# Output plugins (format-specific gstreamer plugins, not detector-geometry code)
# ---------------------------------------------------------------------------
subdir('plugins/hipo')
subdir('plugins/field')
subdir('hipo-histos')

# ---------------------------------------------------------------------------
# Build and install all registered shared-library plugins
# ---------------------------------------------------------------------------
foreach plugin : clas12_plugins
    plugin_target = shared_library(
        plugin['name'],
        plugin['sources'],
        install             : plugin.get('install', true),
        install_dir         : plugin.get('install_dir', get_option('libdir')),
        dependencies        : plugin.get('dependencies', []),
        include_directories : plugin.get('include_directories', []),
        link_with           : plugin.get('link_with', []),
        name_prefix         : '',
        name_suffix         : 'gplugin',
        override_options    : ['b_staticpic=true'],
    )
    clas12_plugin_targets += plugin_target
endforeach

# ---------------------------------------------------------------------------
# CLAS12 magnetic field maps
#
# Download the binary/ascii field maps to <prefix>/fields during `meson install` (skips files
# that already exist). The clas12bin field plugin reads them from the "fields" directory installed
# next to it (<plugin_dir>/../fields), so no FIELD_DIR environment variable is needed at runtime.
# ---------------------------------------------------------------------------
meson.add_install_script(
    python_exe,
    meson.project_source_root() / 'meson' / 'install_fields.py',
    install_tag : 'fields',
)

# ---------------------------------------------------------------------------
# pkg-config file — exposes plugindir so CI can auto-discover installed plugins
#
#   export GEMC_PLUGIN_PATH=$(pkg-config --variable=plugindir clas12-systems)
# ---------------------------------------------------------------------------
configure_file(
    input         : 'clas12-systems.pc.in',
    output        : 'clas12-systems.pc',
    configuration : {
        'PREFIX'    : get_option('prefix'),
        'PLUGINDIR' : get_option('prefix') / get_option('libdir'),
        'VERSION'   : meson.project_version(),
    },
    install       : true,
    install_dir   : get_option('libdir') / 'pkgconfig',
)
