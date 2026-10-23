#!/usr/bin/env python3
"""Construct one detector's generated geometry with the installed GEMC executable."""

from pathlib import Path
from copy import deepcopy
import re
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
    cards = [card]
    if system == "magnets":
        sys.path.insert(0, str(detector))
        from variations import custom_variation_to_run, variation_to_run

        cards = []
        for runno in {**variation_to_run, **custom_variation_to_run}.values():
            case = deepcopy(card)
            case["runno"] = runno
            case["check_overlaps"] = 2
            cards.append(case)
    if system == "beamline":
        sys.path.insert(0, str(detector))
        from variations import custom_variation_to_run, transverse_variation_to_run, variation_to_run

        cards = []
        for variation, runno in {**variation_to_run, **custom_variation_to_run}.items():
            if variation == "TransverseUpstreamBeampipe":
                continue
            case = deepcopy(card)
            case["runno"] = runno
            if variation not in variation_to_run and variation != "ddvcs":
                case["gsystem"] = case["gsystem"][:1]
            cards.append(case)
        transverse = yaml.safe_load((detector / "beamline_transverse.yaml").read_text())
        for runno in transverse_variation_to_run.values():
            case = deepcopy(transverse)
            case["runno"] = runno
            cards.append(case)
    # Fail if geometry generation was omitted or a requested companion system is missing.
    with sqlite3.connect(f"file:{database}?mode=ro", uri=True) as db:
        if system == "beamline":
            named_banks = db.execute(
                "SELECT DISTINCT variation FROM geometry WHERE experiment=? "
                "AND system IN ('beamline', 'beamline_cad', 'beamline_transverse_cad') "
                "AND variation!='default'",
                (card["experiment"],)).fetchall()
            if named_banks:
                raise RuntimeError(f"Beamline SQLite geometry must use the default variation: {named_banks}")
        for case in cards:
            expected = 1  # The Geant4 root volume is added by GEMC.
            for entry in case["gsystem"]:
                count = db.execute(
                    "SELECT COUNT(*) FROM geometry WHERE experiment=? AND system=? AND variation=? AND run=?",
                    (case["experiment"], entry["name"], entry.get("variation", "default"),
                     case["runno"])).fetchone()[0]
                if count == 0:
                    raise RuntimeError(f"No generated geometry for {entry['name']} at run {case['runno']}.")
                expected += count
            case["expected_volumes"] = expected
    with tempfile.TemporaryDirectory(prefix=f"gemc-{system}-") as temp:
        directory = Path(temp)

        # SQLite CAD rows use stls/<mesh>; the directory-based CAD factory uses <system>_cad/.
        meshes = detector / ("cad" if system == "dc" else "stls")
        if meshes.is_dir():
            (directory / "stls").symlink_to(meshes, target_is_directory=True)
            if system == "dc":
                (directory / "cad").symlink_to(meshes, target_is_directory=True)
            (directory / f"{system}_cad").symlink_to(meshes, target_is_directory=True)

        for case in cards:
            expected = case.pop("expected_volumes")
            case.pop("gfields", None)
            case.pop("global_field", None)
            case.update(sql=str(database), n=0, nthreads=1, seed=12345)
            steering = directory / "smoke.yaml"
            steering.write_text(yaml.safe_dump(case, sort_keys=False))
            output = run([str(gemc), str(steering), f"-plugin_path={plugins}"], directory)
            if "references missing mesh" in output or "no mesh file was found" in output:
                raise RuntimeError(f"{system}: GEMC skipped a required CAD mesh:\n{output}")
            if system in ("beamline", "magnets"):
                built = re.search(r"(\d+) geant4 built volumes", output)
                if not built or int(built[1]) != expected:
                    raise RuntimeError(f"Wrong volume count for {system} run {case['runno']}:\n{output}")
            print(f"GEMC constructed {system} run {case['runno']} and loaded its plugins successfully.")


if __name__ == "__main__":
    main()
