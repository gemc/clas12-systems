"""Shared helpers and constants for CLAS12 detector geometry."""

from pathlib import Path

CUSTOM_VARIATION_BLOCK_SIZE = 100

DC_CUSTOM_START = 10000001
CTOF_CUSTOM_START = DC_CUSTOM_START + CUSTOM_VARIATION_BLOCK_SIZE
BEAMLINE_CUSTOM_START = CTOF_CUSTOM_START + CUSTOM_VARIATION_BLOCK_SIZE


def gemc2_fstr(value):
    """Match the GEMC2 Perl fstr helper's default five-digit precision."""
    formatted = f"{value:.5f}".rstrip("0").rstrip(".")
    if formatted == "-0":
        return "0"
    return formatted


def reset_detector_banks(*configurations, obsolete_systems=()):
    """Replace detector and companion SQLite banks; remove retired ASCII exports."""
    for configuration in configurations:
        if configuration.factory == "sqlite":
            systems = (configuration.system, *obsolete_systems)
            placeholders = ",".join("?" for _ in systems)
            with configuration.sqlitedb as db:
                for table in ("geometry", "materials", "mirrors"):
                    columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
                    if {"experiment", "system"} <= columns:
                        db.execute(f"DELETE FROM {table} WHERE experiment=? AND system IN ({placeholders})",
                                   (configuration.experiment, *systems))
        else:
            for system in obsolete_systems:
                for path in Path.cwd().glob(f"{system}__*.txt"):
                    path.unlink()


def index_detector_banks_by_run(*configurations):
    """Store all SQLite banks under default while retaining generation and ASCII labels."""
    for configuration in configurations:
        if configuration.factory != "sqlite":
            continue
        with configuration.sqlitedb as db:
            for table in ("geometry", "materials", "mirrors"):
                columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
                if not {"experiment", "system", "variation", "run"} <= columns:
                    continue
                key = (configuration.experiment, configuration.system)
                ambiguous = db.execute(
                    f"SELECT run FROM {table} WHERE experiment=? AND system=? "
                    "GROUP BY run HAVING COUNT(DISTINCT variation)>1", key).fetchall()
                if ambiguous:
                    raise ValueError(f"{configuration.system} {table} needs distinct run keys: {ambiguous}")
                db.execute(f"UPDATE {table} SET variation='default' WHERE experiment=? AND system=?", key)
