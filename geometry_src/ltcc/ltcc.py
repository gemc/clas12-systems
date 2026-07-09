#!/usr/bin/env python3
from pygemc import autogeometry

from geometry import build_ltcc
from materials import define_materials
from mirrors import define_mirrors
from variations import custom_variation_to_run, variation_to_run


cfg = autogeometry("clas12", "ltcc")

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    define_mirrors(cfg)
    build_ltcc(cfg)
