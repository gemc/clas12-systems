"""LTCC mirror surface definition, ported from clas12Tags geometry_source/ltcc/mirrors.pl.

Every LTCC mirror volume (cylindrical, hyperbolic, elliptical mirrors and, once the
meshes are imported, the Winston cones) names this surface through its `GVolume.mirror`
field.
"""

from pygemc import GMirror

from materials import PENERGY_PMT


# Reflectivity of AlMgF2 coated on thermally shaped acrylic sheets,
# measured by AJRP, 10/01/2012:
REFLECTIVITY_ALMGF2 = (
    "0.8331038 0.8309071 0.8279127 0.8280742 0.8322623 "
    "0.837572 0.8396875 0.8481834 0.8660284 0.8611336 "
    "0.8566167 0.8667431 0.86955 0.8722481 0.8728122 "
    "0.8771635 0.879907 0.879761 0.8831943 0.8894673 "
    "0.8984234 0.9009531 0.8910166 0.8887382 0.8869093 "
    "0.8941976 0.8948479 0.8877356 0.9026919 0.8999685 "
    "0.9101617 0.8983005 0.8991694 0.8990987 0.9000493 "
    "0.9065833 0.9028855 0.8985184 0.9009736 0.9086968 "
    "0.9015145 0.8914838 0.8816829 0.8666895 0.8452400 "
    "0.8293650 0.8095238 0.7857142 0.7579365"
)


def define_mirrors(configuration):
    almgf2 = GMirror("ltcc_AlMgF2")
    almgf2.description = "ltcc mirror reflectivity"
    almgf2.type = "dielectric_metal"
    almgf2.finish = "polished"
    almgf2.model = "unified"
    almgf2.border = "SkinSurface"
    almgf2.photonEnergy = PENERGY_PMT
    almgf2.reflectivity = REFLECTIVITY_ALMGF2
    almgf2.publish(configuration)
