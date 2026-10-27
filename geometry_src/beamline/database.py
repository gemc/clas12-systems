"""Reuse native beamline geometry for its three transverse CAD alternatives."""


def copy_transverse_native_banks(configuration, transverse_runs):
    """Give each transverse CAD run the same native pipes and materials."""
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
