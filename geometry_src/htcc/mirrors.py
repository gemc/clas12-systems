"""HTCC mirror surface definition, ported from clas12Tags geometry_source/htcc/mirrors.pl.

Every HTCC mirror volume and Winston cone names this optical skin surface through its
`GVolume.mirror` field. The reflectivity is AJRP's 10/01/2012 measurement of AlMgF2 on
thermally shaped acrylic sheets, on the 46-point mirror photon-energy grid.
"""

from pygemc import GMirror

from materials import PENERGY_MIRR


# Reflectivity of AlMgF2 coated on thermally shaped acrylic sheets, AJRP 10/01/2012
# (mirrors.pl uses this grazing/normal-incidence table for the mirror skin surface):
REFLECTIVITY_HTCC_ALMGF2 = (
    "0.857039 0.857293 0.856738 0.856274 0.856759 0.857221 "
    "0.857728 0.859595 0.862254 0.860438 0.85846 0.860516 "
    "0.859955 0.85901 0.858631 0.858253 0.858375 0.857274 "
    "0.855112 0.856456 0.857805 0.857126 0.855172 0.852165 "
    "0.849445 0.84416 0.842736 0.839978 0.846421 0.84075 "
    "0.838185 0.836668 0.835591 0.828604 0.826597 0.82482 "
    "0.823019 0.81091 0.805545 0.801419 0.791633 0.787155 "
    "0.754003 0.735616 0.705016 0.722675"
)


def define_mirrors(configuration):
    almgf2 = GMirror("htcc_AlMgF2")
    almgf2.description = "htcc mirror AlMgF2"
    almgf2.type = "dielectric_metal"
    almgf2.finish = "polished"
    almgf2.model = "unified"
    almgf2.border = "SkinSurface"
    almgf2.photonEnergy = PENERGY_MIRR
    almgf2.reflectivity = REFLECTIVITY_HTCC_ALMGF2
    almgf2.publish(configuration)
