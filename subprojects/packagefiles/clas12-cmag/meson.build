project(
  'cMag',
  'c',
  version: '0.1.0',
  default_options: [
    'c_std=c99',
    'warning_level=0',
  ],
)

add_project_arguments('-D_XOPEN_SOURCE=600', '-w', language: 'c')

inc = include_directories('includes')

lib_sources = files(
  'src/maggrid.c',
  'src/magfield.c',
  'src/magfieldutil.c',
  'src/mapcolor.c',
  'src/magfielddraw.c',
  'src/magfieldio.c',
  'src/svg.c',
  'src/testdata.c',
)

lib_cmag = static_library(
  'cMag',
  lib_sources,
  include_directories: inc,
  install: true,
)

cc = meson.get_compiler('c')
m_dep = cc.find_library('m', required: false)

executable(
  'cMagTest',
  'src/main.c',
  include_directories: inc,
  link_with: lib_cmag,
  dependencies: m_dep,
  install: true,
)

install_headers(
  'includes/magfield.h',
  'includes/magfielddraw.h',
  'includes/magfieldio.h',
  'includes/magfieldutil.h',
  'includes/maggrid.h',
  'includes/mapcolor.h',
  'includes/munittest.h',
  'includes/svg.h',
  'includes/testdata.h',
)

clas12_cmag_dep = declare_dependency(
  include_directories: inc,
  link_with: lib_cmag,
  dependencies: m_dep,
)

meson.override_dependency('clas12-cmag', clas12_cmag_dep)
