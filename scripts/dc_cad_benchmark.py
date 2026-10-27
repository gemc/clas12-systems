#!/usr/bin/env python3
"""Offline comparison of repeated CAD meshes against shared sources and copies."""

import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import sqlite3
import statistics
import struct

from beamline_cad_benchmark import primaries, run_case, sha256


def summarize(results):
    """Use only seeds for which both cases completed the requested event count."""
    summary = {}
    for particle in ("loading", "e-", "proton", "pi+", "neutron"):
        rows = [row for row in results if row["particle"] == particle]
        seeds = {row["seed"] for row in rows}
        paired = {seed for seed in seeds if len([
            row for row in rows if row["seed"] == seed and row["completed"]
            and row["reported_events"] == row["events"]]) == 2}
        summary[particle] = {"completed_pairs": len(paired)}
        for label in ("original", "optimized"):
            valid = [row for row in rows if row["case"] == label and row["seed"] in paired]
            summary[particle][label] = {
                key: statistics.median(row[key] for row in valid if row[key] is not None)
                for key in ("wall_seconds", "cpu_seconds", "rss_bytes", "transport_wall_seconds")
                if any(row[key] is not None for row in valid)}
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--originals", type=Path, required=True)
    parser.add_argument("--optimized", type=Path, required=True, help="Collected experiments directory")
    parser.add_argument("--output", type=Path, required=True)
    groups = ("back", "support", "vacuum_jacket", "coil", "hub_cover", "hub_shield", "cold_hub")
    parser.add_argument("--group", choices=groups, default="back")
    parser.add_argument("--events", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--run-manager", choices=("Serial", "MT", "Tasking"),
                        help="Explicit Geant4 run manager, recorded with the measurements")
    parser.add_argument("--keep-going", action="store_true",
                        help="Record failed processes and continue; summarize only completed seed pairs")
    args = parser.parse_args()
    if args.run_manager:
        os.environ["G4RUN_MANAGER_TYPE"] = args.run_manager
    if args.output.exists() or min(args.events, args.repeats) <= 0:
        parser.error("Use a fresh output directory and positive event/repetition counts")
    args.output = args.output.resolve()
    args.output.mkdir(parents=True)
    logs = args.output / "logs"
    logs.mkdir()
    cases, inventories = {}, {}
    magnet_groups = ("vacuum_jacket", "coil", "hub_cover", "hub_shield", "cold_hub")
    optimized_system = "magnets" if args.group in magnet_groups else "dc"
    with sqlite3.connect(args.optimized / "gemc.sqlite") as db:
        if not db.execute("SELECT 1 FROM geometry WHERE system=? AND solid='CAD' LIMIT 1",
                          (optimized_system,)).fetchone():
            optimized_system += "_cad"  # Historical study archives retain their original bank names.
    for label, source, system in (("original", args.originals, "magnets_cad"),
                                   ("optimized", args.optimized, optimized_system)):
        folder = args.output / label
        folder.mkdir()
        shutil.copy2(source / "gemc.sqlite", folder / "geometry.sqlite")
        with sqlite3.connect(folder / "geometry.sqlite") as db:
            for table in ("geometry", "materials", "mirrors"):
                columns = {r[1] for r in db.execute(f"PRAGMA table_info({table})")}
                if {"system", "run", "variation"} <= columns:
                    db.execute(f"DELETE FROM {table} WHERE system!=? OR run!=11 OR variation!='default'",
                               (system,))
            names = tuple(f"dcs{i}r1{args.group}" for i in range(1, 7))
            if args.group == "vacuum_jacket":
                names = tuple(f"shell{i}{part}" for i in range(1, 7) for part in "ab")
                if label == "optimized":
                    names = tuple("vacuumJacket" if name == "shell1a"
                                  else name.replace("shell", "vacuumJacket", 1) for name in names)
            elif args.group == "coil":
                names = tuple("coil" if label == "optimized" and i == 1 else f"coil{i}"
                              for i in range(1, 7))
            elif args.group == "hub_cover":
                names = tuple(f'{"Plate" if label == "original" else "hubCover"}{i}' for i in range(1, 7))
            elif args.group == "hub_shield":
                names = tuple(f"Shield{i}" if label == "original" else
                              ("hub_shield" if i == 2 else f"hub_shield{i}") for i in range(1, 8))
            elif args.group == "cold_hub":
                names = ("Hub001" if label == "original" else "ColdHub",)
            placeholders = ",".join("?" for _ in names)
            db.execute(f"DELETE FROM geometry WHERE name NOT IN ({placeholders})", names)
            rows = db.execute("SELECT name, parameters FROM geometry WHERE solid='CAD'").fetchall()
            assert db.execute("SELECT count(*) FROM geometry").fetchone()[0] == len(names)
            expected = len(names) if label == "original" else (6 if args.group == "vacuum_jacket" else 1)
            if label == "optimized" and args.group == "hub_cover":
                expected = 2
            elif label == "optimized" and args.group == "hub_shield":
                expected = 3
            assert len(rows) == expected
            inventories[label] = {}
            for name, parameters in rows:
                mesh = Path(parameters.split(",")[0].strip())
                assert not mesh.is_absolute() and ".." not in mesh.parts
                target = folder / mesh
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source / mesh, target)
                inventories[label][name] = {"sha256": sha256(target),
                                            "facets": struct.unpack_from("<I", target.read_bytes(), 80)[0]}
        (folder / "benchmark.yaml").write_text(
            "experiment: clas12\nrunno: 11\nnthreads: 1\nphys_list: FTFP_BERT\n"
            f"sql: geometry.sqlite\ngsystem:\n  - name: {system}\n    factory: sqlite\n")
        cases[label] = folder
    acceptance = (2, 15) if args.group == "support" else (5, 45)
    if args.group in ("vacuum_jacket", "coil"):
        acceptance = (5, 70)
    elif args.group == "hub_cover":
        acceptance = (1.5, 5.5)
    elif args.group == "hub_shield":
        acceptance = (0.3, 1.4)
    elif args.group == "cold_hub":
        acceptance = (0.5, 3.0)
    metadata = {"executable": str(args.executable.resolve()), "executable_sha256": sha256(args.executable),
                "platform": platform.platform(), "inventories": inventories,
                "events": args.events, "repeats": args.repeats, "primary_theta_deg": list(acceptance),
                "group": args.group,
                "run_manager": os.environ.get("G4RUN_MANAGER_TYPE", "default"),
                "primary_azimuth_deg": [-180, 180], "momentum_GeV": 5, "field": "off"}
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    results = []
    for particle in ("loading", "e-", "proton", "pi+", "neutron"):
        events = 0 if particle == "loading" else args.events
        for repeat in range(args.repeats):
            seed = 12345 + repeat
            if events:
                primary = primaries(particle, events, seed, acceptance=acceptance)
                for folder in cases.values():
                    (folder / "beam.lund").write_text(primary)
                    (folder / f"{particle}_{seed}.lund").write_text(primary)
            for label in (list(cases) if repeat % 2 == 0 else list(cases)[::-1]):
                row = run_case(args.executable, cases[label], logs, label, particle, events, seed, 0, 1800)
                results.append(row)
                (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
                if not args.keep_going:
                    assert row["completed"] and row["reported_events"] == events, row
    for label, folder in cases.items():
        results.append(run_case(args.executable, folder, logs, label, "overlaps", 0, 12345, 2, 1800))
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    summary = summarize(results)
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    first_log = (logs / results[0]["log"]).read_text()
    version = re.search(r"Geant4 version Name: ([^\n]+)", first_log)
    metadata["geant4_version_banner"] = version[1].strip() if version else "unavailable"
    metadata["failed_processes"] = sum(not row["completed"] for row in results)
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    assert args.keep_going or all(r["completed"] for r in results)
    assert sha256(args.executable) == metadata["executable_sha256"], "Executable changed during measurement"


if __name__ == "__main__":
    main()
