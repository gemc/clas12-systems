#!/usr/bin/env python3
import os

from pygemc import GConfiguration, autogeometry
from pygemc.api.gcad import upload_cad_definitions

from geometry import build_cad_copies, build_ltcc
from materials import define_materials
from mirrors import define_mirrors
from variations import custom_variation_to_run, variation_to_run


all_runs = {**variation_to_run, **custom_variation_to_run}

cfg = autogeometry("clas12", "ltcc")
cad_cfg = GConfiguration("clas12", "ltcc_cad", args=cfg.args)
cad_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stls", "cad__default.yaml")

for variation, run in all_runs.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    define_mirrors(cfg)
    build_ltcc(cfg)

    cad_cfg.init_variation(variation)
    cad_cfg.runno = run
    define_materials(cad_cfg)
    define_mirrors(cad_cfg)
    upload_cad_definitions(cad_yaml, cfg.dbhost, experiment="clas12", variation=variation,
                           run=run, verbosity=0)
    build_cad_copies(cad_cfg)
