"""Shared helpers and constants for CLAS12 detector geometry."""

CUSTOM_VARIATION_BLOCK_SIZE = 100

DC_CUSTOM_START = 10000001
CTOF_CUSTOM_START = DC_CUSTOM_START + CUSTOM_VARIATION_BLOCK_SIZE


def gemc2_fstr(value):
    """Match the GEMC2 Perl fstr helper's default five-digit precision."""
    formatted = f"{value:.5f}".rstrip("0").rstrip(".")
    if formatted == "-0":
        return "0"
    return formatted
