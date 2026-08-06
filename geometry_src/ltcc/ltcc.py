#!/usr/bin/env python3
import os

from pygemc import autogeometry
from pygemc.api.gcad import upload_cad_definitions

from geometry import build_ltcc
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

# CAD volumes (Winston cones + backwall): placement authored declaratively in stls/cad__default.yaml
# and uploaded with the pygemc gcad feature. Variation-independent (always `default`), uploaded once per
# run so any LTCC configuration can load them. The Winston-cone optical surface is resolved per system,
# so ltcc_AlMgF2 is also published under the `stls` system.
cad_yaml = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stls", "cad__default.yaml")

stls_cfg = autogeometry("clas12", "stls", auto_show=False)
stls_cfg.init_variation("default")
for run in all_runs.values():
    stls_cfg.runno = run
    define_mirrors(stls_cfg)                                             # optical surface for the cones
    upload_cad_definitions(cad_yaml, cfg.dbhost, experiment="clas12",    # one row per STL
                           variation="default", run=run, verbosity=0)
