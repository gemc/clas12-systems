# CLAS12 binary mapped magnetic field plugin (solenoid + torus via the cMag library).
#
# Builds the GEMC3 field plugin gfieldclas12binFactory.gplugin. A field definition selects it
# through the generic gfields option node with `type: clas12bin`, e.g.:
#
#   -gfields="[{name: clas12, type: clas12bin, solenoid: Symm_solenoid_..., torus: Symm_torus_...}]"
#
clas12_plugins += [{
    'name'                : 'gfieldclas12binFactory',
    'sources'             : files('gfield_clas12bin.cc'),
    'dependencies'        : [gemc_dep, clas12_cmag_dep, clhep_deps, geant4_core_deps],
    'include_directories' : [include_directories('.')],
}]
