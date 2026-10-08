#!/usr/bin/env python3
"""Construct one detector's generated geometry with the installed GEMC executable."""

from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

import yaml


def run(command, directory):
    result = subprocess.run(command, cwd=directory, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, timeout=300)
    if result.returncode != 0:
        print(result.stdout, file=sys.stderr)
        result.check_returncode()
    return result.stdout


def main():
    gemc, plugins, detector, database = (Path(arg).resolve() for arg in sys.argv[1:])
    system = detector.name
    card = yaml.safe_load((detector / f"{system}.yaml").read_text())
    # Fail if geometry generation was omitted or a requested companion system is missing.
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as db:
        for entry in card["gsystem"]:
            count = db.execute("SELECT COUNT(*) FROM geometry WHERE experiment=? AND system=? AND variation=?",
                               (card["experiment"], entry["name"],
                                entry.get("variation", "default"))).fetchone()[0]
            if count == 0:
                raise RuntimeError(f"No generated geometry for {entry['name']}; run the geometry tests first.")
    with tempfile.TemporaryDirectory(prefix=f"gemc-{system}-") as temp:
        directory = Path(temp)

        # SQLite CAD rows use stls/<mesh>; the directory-based CAD factory uses <system>_cad/.
        meshes = detector / "stls"
        if meshes.is_dir():
            (directory / "stls").symlink_to(meshes, target_is_directory=True)
            (directory / f"{system}_cad").symlink_to(meshes, target_is_directory=True)

        card.pop("gfields", None)
        card.pop("global_field", None)
        card.update(sql=str(database), n=0, nthreads=1, seed=12345)
        steering = directory / "smoke.yaml"
        steering.write_text(yaml.safe_dump(card, sort_keys=False))
        output = run([str(gemc), str(steering), f"-plugin_path={plugins}"], directory)
        if "references missing mesh" in output or "no mesh file was found" in output:
            raise RuntimeError(f"{system}: GEMC skipped a required CAD mesh:\n{output}")
    print(f"GEMC constructed {system} geometry and loaded its plugins successfully.")


if __name__ == "__main__":
    main()
