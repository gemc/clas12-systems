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
cmake_opts.append_compile_args('cpp', '-fPIC')

zlib_dep = dependency('zlib', static : false, required : true)
clhep_deps = dependency('clhep', version : '>=2.4.7.1', include_type : 'system')

geant4_core_dep = dependency('geant4_core', version : '>=11.3.2', method : 'pkg-config')
geant4_core_deps = [geant4_core_dep]

gemc_dep = dependency('gemc', required : get_option('gemc'), include_type : 'system')
if not gemc_dep.found()
    message('GEMC dependency was not found; configure can continue until plugin targets require GEMC headers or libraries.')
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
    ],
)
hipo_cpp_dep = hipo_cpp_sp.get_variable('hipo_dep')

clas12_cmag_dep = dependency('clas12-cmag', include_type : 'system')

