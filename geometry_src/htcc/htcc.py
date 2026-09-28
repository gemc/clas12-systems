#!/usr/bin/env python3
from pygemc import GConfiguration, autogeometry

from geometry import build_cad, build_htcc
from materials import define_materials
from mirrors import define_mirrors
from variations import custom_variation_to_run, variation_to_run


cfg = autogeometry("clas12", "htcc")
cad_cfg = GConfiguration("clas12", "htcc_cad", args=cfg.args)

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    define_mirrors(cfg)
    build_htcc(cfg)

    cad_cfg.init_variation(variation)
    cad_cfg.runno = run
    define_materials(cad_cfg)
    build_cad(cad_cfg)
