#!/usr/bin/env python3

# imports: do not edit these lines
import sys, os, argparse
import logging
import subprocess
from gemc_api_utils import GConfiguration
from gemc_api_geometry import *

from geometry import apply_configuration
from materials import define_materials


_logger = logging.getLogger("pcal")

VARIATION_MAP = {
    "default": "pcal__volumes_default.txt",
    "rga_fall2018": "pcal__volumes_rga_fall2018.txt",
}

def main():
    logging.basicConfig(level=logging.DEBUG)

    # Provides the -h, --help message
    desc_str = "   Will create the clas12 PCAL configuration\n"
    parser = argparse.ArgumentParser(description=desc_str)
    args = parser.parse_args()

    # loop over all the defined builder functions
    for var_key, file_name in VARIATION_MAP.items():

        basepath = os.environ["GEMCDB_ENV"]

        _logger.info(f"Building PCAL configuration for variation {var_key}")
        # Define GConfiguration name, factory and description. Initialize it.
        configuration = GConfiguration('pcal', 'TEXT', 'CLAS12 PCAL')
        configuration.setVariation(var_key)

        # define materials
        configuration.init_mats_file()
        define_materials(configuration)

        # run geometry file bulder for selected variation
        configuration.init_geom_file()
        apply_configuration(f'{basepath}/{file_name}', configuration)
        # print out the GConfiguration
        configuration.printC()


if __name__ == "__main__":
    main()
