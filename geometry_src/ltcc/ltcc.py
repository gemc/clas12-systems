#!/usr/bin/env python3
from pygemc import autogeometry

from geometry import build_cad, build_ltcc
from materials import define_materials
from mirrors import define_mirrors
from variations import custom_variation_to_run, variation_to_run


all_runs = {**variation_to_run, **custom_variation_to_run}

cfg = autogeometry("clas12", "ltcc")

for variation, run in all_runs.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    define_mirrors(cfg)
    build_ltcc(cfg)

# CAD volumes live in the companion `ltcc_cad` system, loaded by GEMC3's CAD
# factory. They are variation-independent (always published under `default`),
# once per run so any LTCC configuration can load them. The Winston-cone mirror
# surface is resolved per system, so ltcc_AlMgF2 is republished here too.
cad_cfg = autogeometry("clas12", "ltcc_cad", auto_show=False)
cad_cfg.init_variation("default")
for run in all_runs.values():
    cad_cfg.runno = run
    define_mirrors(cad_cfg)
    build_cad(cad_cfg)
