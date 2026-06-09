cmake = import('cmake')

sys = host_machine.system()

cmake_opts = cmake.subproject_options()
cmake_opts.add_cmake_defines({
    'BUILD_STATIC_LIBS' : true,
    'BUILD_SHARED_LIBS' : false,
    'ZLIB_USE_STATIC_LIBS' : false,
    'CMAKE_POSITION_INDEPENDENT_CODE' : true,
    'CMAKE_C_STANDARD' : 17,
    'CMAKE_POLICY_VERSION_MINIMUM' : '4.0',
})
cmake_opts.append_compile_args('c',   '-fPIC', '-w')
cmake_opts.append_compile_args('cpp', '-fPIC', '-w')

zlib_dep = dependency('zlib', static : false, required : true)
clhep_deps = dependency('clhep', version : '>=2.4.7.1', include_type : 'system')

geant4_core_dep = dependency('geant4_core', version : '>=11.3.2', method : 'pkg-config', include_type : 'system')
geant4_core_deps = [geant4_core_dep]

gemc_dep = dependency('gemc', required : false, include_type : 'system')

if not gemc_dep.found()
    # pkg-config didn't find gemc — try deriving the prefix from the installed binary.
    _gemc_bin = find_program('gemc', required : false)
    if _gemc_bin.found()
        _gemc_prefix = run_command(
            'sh', '-c',
            'cd "$(dirname "$(dirname "$1")")" && pwd',
            '_', _gemc_bin.full_path(),
            check : false,
        ).stdout().strip()
        if _gemc_prefix != ''
            message('gemc: pkg-config not found; falling back to binary prefix ' + _gemc_prefix)
            # Parse Libs: directly from gemc.pc — pkg-config --libs fails when
            # Requires packages (clhep, Qt6, geant4) are not all in PKG_CONFIG_PATH.
            _gemc_link = run_command(
                'sh', '-c',
                '''pc="$1/lib/pkgconfig/gemc.pc"
                   [ -f "$pc" ] || exit 1
                   p=$(grep "^prefix=" "$pc" | head -1 | cut -d= -f2-)
                   l="${p}/lib"
                   grep "^Libs:" "$pc" | head -1 | sed "s/^Libs://" \
                       | sed "s|\${libdir}|${l}|g; s|\${prefix}|${p}|g"''',
                '_', _gemc_prefix,
                check : false,
            ).stdout().strip().split()
            # Mirror the transitive deps that gemc's pkg-config Requires field
            # normally provides: clhep and geant4_core headers/libs.
            _gemc_transitive = []
            if clhep_deps.found()
                _gemc_transitive += [clhep_deps]
            endif
            if geant4_core_dep.found()
                _gemc_transitive += [geant4_core_dep]
            endif
            gemc_dep = declare_dependency(
                include_directories : [include_directories(_gemc_prefix / 'include')],
                dependencies        : _gemc_transitive,
                link_args           : _gemc_link,
            )
        endif
    endif
endif

if not gemc_dep.found()
    if get_option('gemc').enabled()
        error('GEMC is required (gemc=enabled) but was not found via pkg-config or PATH.')
    else
        message('GEMC dependency was not found; configure can continue until plugin targets require GEMC headers or libraries.')
    endif
elif gemc_dep.type_name() == 'pkgconfig'
    # Belt-and-suspenders for older installations where .pc Cflags had -I${includedir}/gemc.
    # Adding the parent dir ensures "gemc/module/header.h" style includes always resolve.
    gemc_dep = declare_dependency(
        dependencies        : [gemc_dep],
        include_directories : [include_directories(gemc_dep.get_variable(pkgconfig : 'includedir'))],
    )
endif

if sys == 'darwin'
    brew = find_program('brew', required : false)
    if brew.found()
        zstd_prefix = run_command(brew, '--prefix', 'zstd', check : false).stdout().strip()
        openssl_prefix = run_command(brew, '--prefix', 'openssl', check : false).stdout().strip()

        if zstd_prefix != ''
            cmake_opts.append_link_args('-L' + zstd_prefix / 'lib')
            message('Using zstd lib dir: ' + zstd_prefix / 'lib')
        endif

        if openssl_prefix != ''
            cmake_opts.append_link_args('-L' + openssl_prefix / 'lib')
            message('Using openssl lib dir: ' + openssl_prefix / 'lib')
        endif
    endif
endif

ccdb_proj = cmake.subproject('ccdb', options : cmake_opts)
ccdb_dep = ccdb_proj.dependency('ccdb', include_type : 'system')

hipo_cpp_sp = subproject(
    'hipo-cpp',
    default_options : [
        'buildtype=release',
        'default_library=static',
        'cpp_std=c++17',
        'dataframes=false',
        'warning_level=0',
    ],
)
hipo_cpp_dep = hipo_cpp_sp.get_variable('hipo_dep').as_system()

clas12_cmag_dep = dependency('clas12-cmag', include_type : 'system', default_options : ['warning_level=0'])

