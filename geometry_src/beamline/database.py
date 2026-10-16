"""Publish beamline SQLite geometry in the default variation, selected by run number."""

SYSTEMS = ("beamline", "beamline_cad", "beamline_transverse_cad")


def reset_banks(configuration):
    """Replace this detector's banks without disturbing other detectors in an aggregate database."""
    if configuration.factory != "sqlite":
        return
    with configuration.sqlitedb as db:
        for table in ("geometry", "materials"):
            columns = {row[1] for row in db.execute(f"PRAGMA table_info({table})")}
            if {"experiment", "system"} <= columns:
                db.execute(f"DELETE FROM {table} WHERE experiment=? AND system IN (?, ?, ?)",
                           (configuration.experiment, *SYSTEMS))


def index_banks_by_run(configuration, transverse_runs):
    """Retain source labels for authoring/ASCII while storing only default SQLite variations."""
    if configuration.factory != "sqlite":
        return
    with configuration.sqlitedb as db:
        # The three transverse CAD choices need identical native pipes and materials at distinct runs.
        source_run = transverse_runs["noWedges"]
        for table in ("geometry", "materials"):
            columns = [row[1] for row in db.execute(f"PRAGMA table_info({table})") if row[1] != "id"]
            selected = ["?" if column == "run" else column for column in columns]
            for run in transverse_runs.values():
                if run != source_run:
                    db.execute(f"INSERT INTO {table} ({', '.join(columns)}) "
                               f"SELECT {', '.join(selected)} FROM {table} "
                               "WHERE experiment=? AND system='beamline' AND run=?",
                               (run, configuration.experiment, source_run))
        ambiguous = db.execute(
            "SELECT system, run FROM geometry WHERE experiment=? AND system IN (?, ?, ?) "
            "GROUP BY system, run HAVING COUNT(DISTINCT variation) != 1",
            (configuration.experiment, *SYSTEMS)).fetchall()
        if ambiguous:
            raise ValueError(f"Beamline configurations must have distinct run keys: {ambiguous}")
        for table in ("geometry", "materials"):
            db.execute(f"UPDATE {table} SET variation='default' WHERE experiment=? AND system IN (?, ?, ?)",
                       (configuration.experiment, *SYSTEMS))
