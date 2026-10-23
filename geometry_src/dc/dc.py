#!/usr/bin/env python3
from pygemc import GConfiguration, autogeometry

from geometry import build_cad, build_dc
from materials import define_materials
from variations import cad_variation_to_run, custom_variation_to_run, variation_to_run

cfg = autogeometry("clas12", "dc")

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    build_dc(cfg)

# The back membranes and supports are unchanged across runs. Publish exact keys for each configuration
# they previously belonged to, as well as DC's custom DDVCS configuration.
cad_cfg = GConfiguration("clas12", "dc_cad", args=cfg.args)
if cad_cfg.factory == "sqlite":
    with cad_cfg.sqlitedb as db:
        db.execute("DELETE FROM geometry WHERE experiment=? AND system='dc_cad'", (cad_cfg.experiment,))
for variation, run in cad_variation_to_run.items():
    cad_cfg.init_variation(variation)
    cad_cfg.runno = run
    build_cad(cad_cfg)

if cad_cfg.factory == "sqlite":
    with cad_cfg.sqlitedb as db:
        db.execute("UPDATE geometry SET variation='default' WHERE experiment=? AND system='dc_cad'",
                   (cad_cfg.experiment,))
