#!/usr/bin/env python3
from pygemc import autogeometry

from geometry import build_ftof
from materials import define_materials
from variations import custom_variation_to_run, variation_to_run


cfg = autogeometry("clas12", "ftof")

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    build_ftof(cfg)
