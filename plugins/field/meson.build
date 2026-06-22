# CLAS12 binary mapped magnetic field plugin (solenoid + torus via the cMag library).
#
# Builds the GEMC3 field plugin gfieldclas12-cmagFactory.gplugin. A field definition selects it
# through the generic gfields option node with `type: clas12-cmag`, e.g.:
#
#   -gfields="[{name: clas12, type: clas12-cmag, solenoid: Symm_solenoid_..., torus: Symm_torus_...}]"
#
clas12_plugins += [{
    'name'                : 'gfieldclas12-cmagFactory',
    'sources'             : files('gfield_clas12bin.cc'),
    'dependencies'        : [gemc_plugin_dep, clas12_cmag_dep],
    'include_directories' : [include_directories('.')],
}]
