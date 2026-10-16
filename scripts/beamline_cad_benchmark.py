#!/usr/bin/env python3
"""Offline GEMC3 comparison of original and optimized beamline CAD groups on macOS.

Use one benchmark process at a time. Both fixtures load only the selected group, with identical
materials, placements, primary files and physics. This measures the group, not complete CLAS12 performance.
"""

import argparse
from collections import Counter
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import re
import shutil
import signal
import sqlite3
import statistics
import subprocess
import time

REPO = Path(__file__).resolve().parents[1]
PAIRS = {
    "apex": {"Apex_Shield_Lead_Fill": "Apex_Shield_Lead_Fill",
             "Apex_Shield_Hub": "Apex_Shield_PCAL_Hub"},
    "downstream": {name: name for name in ("Downstream_Beam_tube_Segment_1",
                                           "Downstream_Beam_tube_Segment_2")},
    "exit": {"Beamline_Adapter_1": "Torus_Beam_Tube_Reducer_2",
             "Torus_Exit_Shield_Casing": "Torus_Exit_Shield_Casing",
             "Torus_Exit_Shield_Lead_Fill": "Torus_Exit_Shield_Lead_Fill"},
    "adjuster": {name: name for name in ("adjuster1", "adjuster2", "adjuster3")},
    "inner_shield": {"FTInnerShieldAndFlange": "innerShieldAndFlange"},
    "bolts": {f"FTInnerShieldAndFlange_Bolt{i}": f"nut{i}" for i in range(1, 10)},
    "outer_flange": {"FTOuterFlange": "outerFlange"},
    "outer_mount": {"FTOuterMount": "outerMount"},
    "ft_inner_shield": {"FTInnerShield": "taggerInnerShield"},
    "moller_cone": {"moller_cone": "main-cone"},
    "cone_tip": {"moller_cone_tip": "cone-tip"},
    "ft_flange": {"FTFlange": "flange-assembly"},
    "extension_inner": {"moller-cone-extension-inner": "inner-assembly"},
    "extension_lead": {"moller-cone-extension-lead-fill": "lead-shield"},
    "extension_case": {"moller-cone-extension-lead-case": "outer-assembly"},
    "extension_tungsten": {"moller-cone-extension-tungsten-addon": "outer-cone"},
    "ft_joints": {name: name for name in (
        "moller-cone-extension-inner", "moller-cone-extension-lead-case", "moller-cone-extension-lead-fill",
        "moller-cone-extension-tungsten-addon", "moller_cone", "moller_cone_tip", "FTFlange", "FTInnerShield")},
    "downstream_joints": {name: name for name in ("Beamline_Adapter_1", "Downstream_Beam_tube_Segment_1",
                                                "Downstream_Beam_tube_Segment_2")},
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primaries(particle, events, seed, acceptance=(0.25, 3.5), azimuth=(-180, 180)):
    """Five-GeV primaries from the target, uniform in solid angle over the pair's acceptance."""
    pdg, mass = {"e-": (11, 0.000510999), "proton": (2212, 0.938272),
                 "pi+": (211, 0.139570), "neutron": (2112, 0.939565), "geantino": (0, 0)}[particle]
    rng = random.Random(seed)
    lines = []
    for _ in range(events):
        cosine = rng.uniform(math.cos(math.radians(acceptance[1])), math.cos(math.radians(acceptance[0])))
        phi = rng.uniform(math.radians(azimuth[0]), math.radians(azimuth[1]))
        sine = math.sqrt(1 - cosine * cosine)
        px, py, pz = 5 * sine * math.cos(phi), 5 * sine * math.sin(phi), 5 * cosine
        lines.extend(["1 1 1 0 0 0 0 0 0 0",
                      f"1 0 1 {pdg} 0 0 {px:.12g} {py:.12g} {pz:.12g} "
                      f"{math.sqrt(25 + mass * mass):.12g} {mass} 0 0 0"])
    return "\n".join(lines) + "\n"


def run_case(executable, folder, logs, label, particle, events, seed, overlaps, timeout):
    tag = f"{label}_{particle}_n{events}_seed{seed}_overlaps{overlaps}"
    log, usage = logs / (tag + ".log"), logs / (tag + ".time")
    cmd = [str(executable), "benchmark.yaml", f"-n={events}", f"-seed={seed}",
           f"-check_overlaps={overlaps}", "-log_every=1000000"]
    if events:
        cmd.append('-gparticlefile=[{format: lund, filename: beam.lund}]')
    started = time.perf_counter()
    with log.open("w") as stream:
        process = subprocess.Popen(["/usr/bin/time", "-l", "-o", str(usage), *cmd],
                                   cwd=folder, stdout=stream, stderr=subprocess.STDOUT,
                                   start_new_session=True)
        try:
            code = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = "timeout"
    content = re.sub(r"\x1b\[[0-9;]*m", "", log.read_text(errors="replace"))
    timing = usage.read_text()
    cpu = re.search(r"([\d.]+)\s+user\s+([\d.]+)\s+sys", timing)
    memory = re.search(r"(\d+)\s+maximum resident set size", timing)
    total = re.search(r"total simulation time ([\d.e+-]+) seconds", content)
    beam = re.search(r"total time since beamOn was issued ([\d.e+-]+) seconds", content)
    completed_events = re.search(r"events / second \((\d+) events", content)
    result = {"case": label, "particle": particle, "events": events, "seed": seed,
              "overlaps": overlaps, "exit_code": code, "wall_seconds": time.perf_counter() - started,
              "cpu_seconds": sum(map(float, cpu.groups())) if cpu else None,
              "rss_bytes": int(memory[1]) if memory else None,
              "simulation_wall_seconds": float(total[1]) if total else None,
              "transport_wall_seconds": float(beam[1]) if beam else None,
              "reported_events": int(completed_events[1]) if completed_events else 0,
              "exception_codes": dict(Counter(re.findall(r"\*\*\* G4Exception : (\S+)", content))),
              "completed": code == 0 and "Simulation completed, arrivederci!" in content,
              "command": cmd, "log": log.name, "time_report": usage.name,
              "primary_sha256": sha256(folder / "beam.lund") if events else None}
    print(json.dumps(result), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--executable", type=Path, required=True)
    parser.add_argument("--database", type=Path, required=True, help="Generated beamline SQLite database")
    parser.add_argument("--originals", type=Path, required=True, help="Archived original meshes")
    parser.add_argument("--pair", choices=tuple(PAIRS), default="apex")
    parser.add_argument("--runno", type=int, default=11,
                        help="Source database run key (tip, flange, and extension groups use 5874)")
    parser.add_argument("--filled-reference", type=Path,
                        help="Alternate baseline STL for a repaired or fixed-volume comparison")
    parser.add_argument("--baseline-description",
                        help="Describe the alternate baseline supplied with --filled-reference")
    parser.add_argument("--optimized", type=Path, default=REPO / "geometry_src/beamline/stls")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--events", type=int, default=10000)
    parser.add_argument("--repeats", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=1800)
    args = parser.parse_args()
    if args.filled_reference and args.pair not in (
            "outer_flange", "ft_inner_shield", "moller_cone", "extension_inner", "extension_tungsten"):
        parser.error("--filled-reference applies only to the flange, FT shield, cone, or repaired extensions")
    if args.baseline_description and not args.filled_reference:
        parser.error("--baseline-description requires --filled-reference")
    names = PAIRS[args.pair]
    acceptance = {"apex": (0.25, 3.5), "downstream": (0.1, 1.3), "exit": (0.25, 2.6),
                  "adjuster": (2.5, 3.3), "inner_shield": (0.25, 3.0), "bolts": (1.3, 3.0),
                  "outer_flange": (1.9, 2.8), "outer_mount": (1.5, 2.4),
                  "ft_inner_shield": (0.7, 2.7), "moller_cone": (1.1, 2.6),
                  "cone_tip": (2.5, 4.8),
                  "ft_flange": (1.4, 3.8),
                  "extension_inner": (0.8, 1.8),
                  "extension_lead": (1.6, 4.5),
                  "extension_case": (3.7, 4.8),
                  "extension_tungsten": (2.7, 5.0),
                  "ft_joints": (0.8, 4.8),
                  "downstream_joints": (0.1, 1.3)}[args.pair]
    azimuth = (-95, -85) if args.pair == "adjuster" else (-180, 180)
    if min(args.events, args.repeats, args.timeout, args.runno) <= 0 or args.output.exists():
        parser.error("Positive counts and a fresh output directory are required")
    args.executable = args.executable.resolve()
    args.output.mkdir(parents=True)
    logs = args.output / "logs"
    logs.mkdir()
    card = (f"experiment: clas12\nrunno: {args.runno}\nnthreads: 1\nphys_list: FTFP_BERT\n"
            "sql: geometry.sqlite\ngsystem:\n  - name: beamline_cad\n    factory: sqlite\n")
    cases = {}
    for label in ("original", "optimized"):
        folder = args.output / label
        (folder / "stls").mkdir(parents=True)
        shutil.copy2(args.database, folder / "geometry.sqlite")
        with sqlite3.connect(folder / "geometry.sqlite") as db:
            selected = list(set(names) | set(names.values()))
            if args.pair == "adjuster":
                selected.append("ft_adjuster")
            placeholders = ", ".join("?" for _ in selected)
            db.execute("DELETE FROM geometry WHERE system != 'beamline_cad' OR run != ? "
                       f"OR variation != 'default' OR name NOT IN ({placeholders})", [args.runno, *selected])
            assets = names
            if args.pair == "adjuster":
                columns = [r[1] for r in db.execute("PRAGMA table_info(geometry)") if r[1] != "id"]
                rows = [dict(zip(columns, r)) for r in db.execute(
                    "SELECT " + ", ".join(columns) + " FROM geometry ORDER BY name")]
                if len(rows) not in (1, 3):
                    raise ValueError("Expected the original adjuster trio or its merged replacement")
                physical = [{k: v for k, v in r.items() if k not in ("name", "parameters")} for r in rows]
                if any(r != physical[0] for r in physical):
                    raise ValueError("Adjuster materials and placements must agree")
                assets = names if label == "original" else {"ft_adjuster": "ft_adjuster"}
                db.execute("DELETE FROM geometry")
                for name in assets:
                    row = {**rows[0], "name": name, "parameters": f"stls/{name}.stl, 1"}
                    db.execute("INSERT INTO geometry (" + ", ".join(columns) + ") VALUES (" +
                               ", ".join("?" for _ in columns) + ")", [row[c] for c in columns])
            else:
                for name, original in names.items():
                    if name != original:
                        db.execute("UPDATE geometry SET name=?, parameters=? WHERE name=?",
                                   (name, f"stls/{name}.stl, 1", original))
            if db.execute("SELECT count(*) FROM geometry").fetchone()[0] != len(assets):
                raise ValueError("Expected exactly the selected group's CAD rows")
        for name, original in assets.items():
            path = (args.originals / (original + ".stl") if label == "original"
                    else args.optimized / (name + ".stl"))
            if label == "original" and args.filled_reference:
                path = args.filled_reference
            shutil.copy2(path, folder / "stls" / (name + ".stl"))
        (folder / "benchmark.yaml").write_text(card)
        cases[label] = folder
    metadata = {"date": time.strftime("%Y-%m-%d"), "platform": platform.platform(),
                "executable": str(args.executable), "executable_sha256": sha256(args.executable),
                "version": subprocess.check_output([str(args.executable), "--version"], text=True),
                "arguments": {k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()},
                "card": card, "physics": "FTFP_BERT, no optical processes, no magnetic field",
                "pair": args.pair, "primary_acceptance_deg": list(acceptance), "momentum_GeV": 5,
                "primary_azimuth_deg": list(azimuth),
                "mesh_hashes": {label: {p.name: sha256(p) for p in (folder / "stls").glob("*.stl")}
                                for label, folder in cases.items()}}
    if args.filled_reference:
        default_description = (
            "Hole-filled, unreduced flange; same material volume as optimized" if args.pair == "outer_flange"
            else "Smooth-flange FT inner shield before protected decimation; "
                 "grooves and central passage retained")
        if args.pair == "moller_cone":
            default_description = (
                "Hole-filled Moller cone with enlarged counterbore before protected decimation")
        if args.pair == "extension_inner":
            default_description = "Inner extension with its radial-port wall repaired before decimation"
        if args.pair == "extension_tungsten":
            default_description = (
                "Tungsten add-on with its inclined radial-port wall repaired before decimation")
        metadata["baseline_description"] = args.baseline_description or default_description
    (args.output / "metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    results = []
    for particle in ("loading", "e-", "proton", "pi+", "neutron"):
        events = 0 if particle == "loading" else args.events
        for repeat in range(args.repeats):
            seed = 12345 + repeat
            if events:
                primary = primaries(particle, events, seed, acceptance, azimuth)
                for folder in cases.values():
                    (folder / "beam.lund").write_text(primary)
                    (folder / f"{particle}_{seed}.lund").write_text(primary)
            for label in (list(cases) if repeat % 2 == 0 else list(cases)[::-1]):
                result = run_case(args.executable, cases[label], logs, label,
                                  particle, events, seed, 0, args.timeout)
                results.append(result)
                (args.output / "results.json").write_text(json.dumps(results, indent=2) + "\n")
                if not result["completed"] or result["reported_events"] != events:
                    raise SystemExit("Run failed or event count differs; inspect the retained logs")
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
