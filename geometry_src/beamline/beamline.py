#!/usr/bin/env python3
"""Generate all beamline native and CAD variations without a sensitive plugin."""

from copy import copy

from pygemc import GConfiguration, autogeometry

from clas12_common import index_detector_banks_by_run, reset_detector_banks
from database import copy_transverse_native_banks
from geometry import build_beamline, build_cad
from materials import define_materials
from variations import custom_variation_to_run, transverse_variation_to_run, variation_to_run


cfg = autogeometry("clas12", "beamline")
cad_cfg = GConfiguration("clas12", "beamline_cad", args=cfg.args)
transverse_args = copy(cfg.args)
transverse_args.variation = "noWedges"
transverse_cfg = GConfiguration("clas12", "beamline_transverse_cad", args=transverse_args)
reset_detector_banks(cfg, cad_cfg, transverse_cfg)

for variation, run in {**variation_to_run, **custom_variation_to_run}.items():
    cfg.init_variation(variation)
    cfg.runno = run
    define_materials(cfg)
    build_beamline(cfg)

    # The GEMC2 source provides CAD placements for the ten standard runs and DDVCS.
    if variation in variation_to_run or variation == "ddvcs":
        cad_cfg.init_variation(variation)
        cad_cfg.runno = run
        define_materials(cad_cfg)
        build_cad(cad_cfg)

for variant, run in transverse_variation_to_run.items():
    transverse_cfg.init_variation(variant)
    transverse_cfg.runno = run
    build_cad(transverse_cfg, transverse=True)

copy_transverse_native_banks(cfg, transverse_variation_to_run)
index_detector_banks_by_run(cfg, cad_cfg, transverse_cfg)
