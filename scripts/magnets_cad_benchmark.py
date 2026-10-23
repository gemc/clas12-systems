#!/usr/bin/env python3
"""Offline GEMC3 before/after benchmarks for magnets CAD optimization.

Supply an archived pre-change experiments directory. The dedup study retains beamline and solenoid and
removes only nine DSShield placements and apex. The plate study isolates the downstream plate and jacket.
"""

import argparse
import json
from pathlib import Path
import platform
import shutil
import sqlite3
import statistics
import struct

from beamline_cad_benchmark import primaries, run_case, sha256


REMOVED = (
    "DSShieldBackAss", "DSShieldBackCover", "DSShieldBackLead", "DSShieldFlange",
    "DSShieldFlangeAttachment", "DSShieldFrontAss", "DSShieldFrontCover", "DSShieldFrontLead",
    "DSShieldInnerAss", "apex",
)
PLATE_PARTS = ("DownstreamShieldingPlate", "DownstreamVacuumJacket")
SYSTEMS = ("beamline", "beamline_cad", "solenoid", "magnets_cad")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--originals", type=Path, required=True, help="Pre-change experiments directory")
    parser.add_argument("--study", choices=("dedup", "plate", "upstream_plate"), default="dedup")
    parser.add_argument("--optimized", type=Path, help="Optimized STL directory; required for --study plate")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=200)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    if min(args.events, args.repeats, args.timeout) <= 0 or args.output.exists():
        parser.error("Positive counts and a fresh output directory are required")
    if args.study != "dedup" and not args.optimized:
        parser.error("Plate studies require --optimized")
    args.executable = args.executable.resolve(strict=True)
    args.originals = args.originals.resolve(strict=True)
    args.output = args.output.resolve()
    args.output.mkdir(parents=True)
    logs = args.output / "logs"
    logs.mkdir()
    cases = {}
    inventories = {}
    systems = SYSTEMS if args.study == "dedup" else ("magnets_cad",)
    acceptance = (0.25, 3.5) if args.study == "dedup" else (0.5, 3.2)
    plate_parts = PLATE_PARTS
    if args.study == "upstream_plate":
        plate_parts = tuple(name.replace("Downstream", "Upstream") for name in PLATE_PARTS)
        acceptance = (1.0, 5.2)
    for label in ("original", "optimized"):
        folder = args.output / label
        folder.mkdir()
        database = folder / "geometry.sqlite"
        shutil.copy2(args.originals / "gemc.sqlite", database)
        with sqlite3.connect(database) as db:
            placeholders = ",".join("?" for _ in systems)
            for table in ("geometry", "materials", "mirrors"):
                columns = {r[1] for r in db.execute(f"PRAGMA table_info({table})")}
                if not {"system", "run", "variation"} <= columns:
                    if db.execute(f"SELECT count(*) FROM {table}").fetchone()[0]:
                        raise ValueError(f"Unexpected populated table without bank keys: {table}")
                    continue
                db.execute(f"DELETE FROM {table} WHERE system NOT IN ({placeholders}) "
                           "OR run != 11 OR variation != 'default'", systems)
            names = {r[0] for r in db.execute("SELECT name FROM geometry WHERE system='magnets_cad'")}
            expected = 61 if args.study == "dedup" else 51
            selected = REMOVED if args.study == "dedup" else plate_parts
            if len(names) != expected or not set(selected) <= names:
                raise ValueError(f"Expected the pre-change {expected}-piece magnets CAD bank")
            if args.study != "dedup":
                db.execute("DELETE FROM geometry WHERE name NOT IN (?,?)", plate_parts)
                columns = [r[1] for r in db.execute("PRAGMA table_info(geometry)") if r[1] != "id"]
                parts = [dict(zip(columns, row)) for row in db.execute(
                    "SELECT " + ",".join(columns) + " FROM geometry ORDER BY name")]
                physical = [{k: v for k, v in row.items() if k not in ("name", "parameters")} for row in parts]
                if len(parts) != 2 or physical[0] != physical[1]:
                    raise ValueError("Plate and jacket must share their material and placement")
            elif label == "optimized":
                db.executemany("DELETE FROM geometry WHERE system='magnets_cad' AND name=?",
                               [(name,) for name in REMOVED])
            rows = db.execute("SELECT system, name, parameters FROM geometry WHERE solid='CAD'").fetchall()
            inventory = {}
            for system, name, parameters in rows:
                mesh = Path(parameters.split(",")[0].strip())
                if mesh.is_absolute() or ".." in mesh.parts:
                    raise ValueError(f"Expected collected relative mesh path: {mesh}")
                target = folder / mesh
                target.parent.mkdir(parents=True, exist_ok=True)
                source = (args.optimized / f"{name}.stl" if args.study != "dedup" and label == "optimized"
                          else args.originals / mesh)
                shutil.copy2(source, target)
                data = target.read_bytes()
                triangles = struct.unpack_from("<I", data, 80)[0]
                if len(data) != 84 + 50 * triangles:
                    raise ValueError(f"Expected binary STL: {mesh}")
                inventory[f"{system}/{name}"] = {"sha256": sha256(target), "triangles": triangles,
                                                "bytes": len(data), "path": str(mesh)}
            inventories[label] = inventory
        card = ("experiment: clas12\nrunno: 11\nnthreads: 1\nphys_list: FTFP_BERT\n"
                "sql: geometry.sqlite\ngsystem:\n" +
                "".join(f"  - name: {system}\n    factory: sqlite\n" for system in systems))
        (folder / "benchmark.yaml").write_text(card)
        cases[label] = folder
    metadata = {"executable": str(args.executable), "executable_sha256": sha256(args.executable),
                "platform": platform.platform(), "originals": str(args.originals),
                "source_database_sha256": sha256(args.originals / "gemc.sqlite"),
                "study": args.study, "removed": list(REMOVED) if args.study == "dedup" else [],
                "changed_meshes": list(plate_parts) if args.study != "dedup" else [],
                "events": args.events, "repeats": args.repeats,
                "runno": 11, "systems": list(systems), "momentum_GeV": 5,
                "primary_theta_deg": list(acceptance), "primary_azimuth_deg": [-180, 180],
                "field": "off", "inventories": inventories}
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
                result = run_case(args.executable, cases[label], logs, label, particle,
                                  events, seed, 0, args.timeout)
                results.append(result)
                (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
                if not result["completed"] or result["reported_events"] != events:
                    raise SystemExit("Run failed or event count differs; inspect retained logs")
    for label, folder in cases.items():
        results.append(run_case(args.executable, folder, logs, label, "overlaps", 0, 12345, 2, args.timeout))
    (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    summary = {}
    for particle in ("loading", "e-", "proton", "pi+", "neutron"):
        summary[particle] = {}
        for label in cases:
            rows = [r for r in results if r["particle"] == particle and r["case"] == label]
            summary[particle][label] = {
                key: statistics.median(r[key] for r in rows if r[key] is not None)
                for key in ("wall_seconds", "cpu_seconds", "rss_bytes", "simulation_wall_seconds",
                            "transport_wall_seconds") if any(r[key] is not None for r in rows)}
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    if sha256(args.executable) != metadata["executable_sha256"]:
        raise SystemExit("Executable changed during measurement; do not use these timings")
    if any(not r["completed"] for r in results):
        raise SystemExit("Construction diagnostics failed; inspect results.json")


if __name__ == "__main__":
    main()
