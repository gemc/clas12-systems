#!/usr/bin/env python3
from pygemc import GConfiguration, autogeometry

from clas12_common import index_detector_banks_by_run, reset_detector_banks
from geometry import build_cad, build_ltcc
from materials import define_materials
from mirrors import define_mirrors
from variations import custom_variation_to_run, variation_to_run


cfg = autogeometry("clas12", "ltcc")
cad_cfg = GConfiguration("clas12", "ltcc_cad", args=cfg.args)
reset_detector_banks(cfg, cad_cfg)

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    define_mirrors(cfg)
    build_ltcc(cfg)

    cad_cfg.init_variation(variation)
    cad_cfg.runno = run
    define_materials(cad_cfg)
    define_mirrors(cad_cfg)
    build_cad(cad_cfg)

index_detector_banks_by_run(cfg, cad_cfg)
