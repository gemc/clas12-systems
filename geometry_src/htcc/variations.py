"""Local CLAS12 run and variation mapping used by the HTCC geometry builder.

The three variations mirror `clas12Tags/geometry_source/htcc/htcc.pl`: they share the
same shapes and differ only by a small global z-shift of the gas volume and windows
(applied in geometry.py). Run numbers follow the other clas12-systems ports.
"""

variation_to_run = {
    "default": 11,
    "rga_spring2018": 3029,
    "rga_fall2018": 4763,
}

custom_variation_to_run = {}
