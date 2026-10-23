"""Solenoid polycone dimensions in millimetres, from GEMC2 solenoid.pl."""

INNER_RADII = (536.25,) + (390,) * 12 + (784,)
OUTER_RADII = (1020, 1020, 1038, 1038, 1020, 1020, 1038, 1038, 1020, 1020, 1038, 1038, 1020, 1020)
Z_PLANES = (0, 425, 440.7, 546.4, 562.1, 814.92, 830.62, 936.32, 952.02,
            1204.84, 1220.54, 1326.24, 1341.94, 1783.44)
Z_START = -898.093
Z_SHIFTS = {"default": 0, "rga_spring2018": -1.94, "rga_fall2018": -3.0}
