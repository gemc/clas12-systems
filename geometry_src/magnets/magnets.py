#!/usr/bin/env python3
"""Generate the native solenoid and all magnets CAD configurations from GEMC2."""

from pygemc import GConfiguration, autogeometry

from geometry import build_cad, build_solenoid
from materials import define_materials
from variations import custom_variation_to_run, variation_to_run


cfg = autogeometry("clas12", "solenoid")
cad_cfg = GConfiguration("clas12", "magnets_cad", args=cfg.args)
systems = (cfg.system, cad_cfg.system)

if cfg.factory == "sqlite":
    with cfg.sqlitedb as db:
        for table in ("geometry", "materials"):
            columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
            if {"experiment", "system"} <= columns:
                db.execute(f"DELETE FROM {table} WHERE experiment=? AND system IN (?, ?)",
                           (cfg.experiment, *systems))

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    build_solenoid(cfg)

    cad_cfg.init_variation(variation)
    cad_cfg.runno = run
    define_materials(cad_cfg)
    build_cad(cad_cfg)

# GEMC2 selects these configurations by run, with the SQLite variation always default.
if cfg.factory == "sqlite":
    with cfg.sqlitedb as db:
        for table in ("geometry", "materials"):
            db.execute(f"UPDATE {table} SET variation='default' WHERE experiment=? AND system IN (?, ?)",
                       (cfg.experiment, *systems))
