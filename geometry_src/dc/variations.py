"""Local CLAS12 run and variation mapping used by the DC geometry builder."""

RUNS_BY_VARIATION = {
    "default": [11],
    "rga_spring2018": [3029],
    "rga_fall2018": [4763],
    "rga_spring2019": [6608, 15016, 15534, 15628],
    "rgb_spring2019": [6150],
    "rgb_fall2019": [11093, 15043, 15434, 15566],
    "rgb_spring2020": [11323],
    "rgc_summer2022": [16000],
    "rgc_fall2022": [16843],
    "rge_spring2024_Empty_Al": [20506],
    "rge_spring2024_Empty_C": [20014, 20070],
    "rge_spring2024_Empty_Empty": [20035, 20507],
    "rge_spring2024_Empty_Pb": [20269],
    "rge_spring2024": [20000],
    "rge_spring2024_LD2_Al": [20435],
    "rge_spring2024_LD2_C": [20021, 20131, 20508],
    "rge_spring2024_LD2_Cu": [20177],
    "rge_spring2024_LD2_Pb": [20041, 20074, 20232, 20282, 20494, 20520],
    "rge_spring2024_LD2_Sn": [20331],
    "rgk_fall2018": [5674],
    "rgk_winter2018": [5874],
    "rgk_fall2023": [19200],
    "rgk_spring2024": [19300],
    "rgf_spring2020": [11620],
    "rgf_summer2020": [12389],
    "rgm_fall2021_H": [15016],
    "rgm_fall2021_He": [15108, 15458],
    "rgm_fall2021_C_S": [15643, 15733],
    "rgm_fall2021_C_L": [15766, 15778],
    "rgm_fall2021_Ar": [15671, 15734, 15789],
    "rgm_fall2021_Cx4": [15178],
    "rgm_fall2021_Ca": [15356, 15829],
    "rgm_fall2021_Sn_L": [15804],
    "rgm_fall2021_Snx4": [15318],
    "rgd_fall2023": [18304],
    "rgd_fall2023_lD2": [18305, 18318, 18419, 18528, 18644, 18764, 18851, 19021],
    "rgd_fall2023_CuSn": [18347, 18372, 18560, 18660, 18874, 19061],
    "rgd_fall2023_CxC": [18339, 18369, 18400, 18440, 18756, 18796],
    "rgd_fall2023_empty": [18399, 19060, 18316],
    "rgl_spring2025": [21000],
    "rgl_spring2025_H2": [21001],
    "rgl_spring2025_D2": [21002],
    "rgl_spring2025_He": [21003],
}

CUSTOM_VARIATIONS = {
    "pbtest",
    "ND3",
    "hdice",
    "longitudinal",
    "transverse",
    "ddvcs",
    "rghFTOut",
    "rghFTOn",
    "TransverseUpstreamBeampipe",
    "michel_9mmcopper",
}

DC_GEOMETRY_SOURCE_RUN = 11
DC_SQLITE_VARIATIONS = ("default",)
DC_TEXT_VARIATIONS = ("default", "ddvcs")


def runs_for_variation(variation):
    """Return the local CLAS12 run list for a variation."""
    return RUNS_BY_VARIATION.get(variation, [])


def geometry_source_variation(variation):
    """Return the coatjava variation to use for the requested DC variation."""
    if variation == "original":
        raise ValueError("The obsolete DC 'original' variation is intentionally not supported.")
    if variation == "ddvcs":
        return "default"
    return variation


def geometry_source_run(_variation, requested_run):
    """Return the CCDB run used by coatjava for DC geometry."""
    if requested_run not in (None, 1, "1"):
        return int(requested_run)
    return DC_GEOMETRY_SOURCE_RUN
