#!/usr/bin/env python3
from pygemc import autogeometry

from geometry import build_dc
from materials import define_materials
from variations import geometry_source_run

cfg = autogeometry("clas12", "dc")
cfg.runno = geometry_source_run(cfg.variation, cfg.runno)

define_materials(cfg)
build_dc(cfg)
