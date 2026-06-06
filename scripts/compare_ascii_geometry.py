#!/usr/bin/env python3
"""Compare generated CLAS12 systems ASCII geometry with clas12Tags references."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


REPO_ROOT = Path(__file__).resolve().parents[1]
GEOMETRY_SRC = REPO_ROOT / "geometry_src"
DEFAULT_CLAS12TAGS = REPO_ROOT.parent / "clas12Tags" / "geometry_source"
EXCLUDED_SYSTEM_DIRS = {"coatjava", "coatjava_src", "coatjava_factories"}
GEOMETRY_FIELDS = (
    "name",
    "mother",
    "description",
    "position",
    "rotation",
    "solid",
    "dimensions",
    "material",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate ASCII geometry for local systems and compare it with clas12Tags references.",
    )
    parser.add_argument(
        "systems",
        nargs="*",
        help="Systems to compare. Defaults to every geometry_src/<system>/<system>.py found.",
    )
    parser.add_argument("-v", "--variation", default="default", help="Local variation to generate.")
    parser.add_argument(
        "--reference-variation",
        help="clas12Tags variation name. Defaults to --variation.",
    )
    parser.add_argument("-r", "--run", type=int, help="Run number passed to the local geometry script.")
    parser.add_argument(
        "--clas12tags",
        type=Path,
        default=DEFAULT_CLAS12TAGS,
        help=f"clas12Tags geometry_source directory. Default: {DEFAULT_CLAS12TAGS}",
    )
    parser.add_argument(
        "--python",
        type=Path,
        default=default_python(),
        help="Python executable used to run system scripts.",
    )
    parser.add_argument(
        "--workdir",
        type=Path,
        help="Directory for generated ASCII files. Defaults to a temporary directory.",
    )
    parser.add_argument("--keep", action="store_true", help="Keep the generated work directory.")
    parser.add_argument("--diff", action="store_true", help="Print field-level differences for mismatches.")
    return parser


def default_python() -> Path:
    venv_python = REPO_ROOT / "build" / "subprojects" / "pygemc" / "python_env" / "bin" / "python3"
    if venv_python.exists():
        return venv_python
    return Path(sys.executable)


def discover_systems() -> list[str]:
    systems = []
    for child in sorted(GEOMETRY_SRC.iterdir()):
        if not child.is_dir() or child.name in EXCLUDED_SYSTEM_DIRS:
            continue
        if (child / f"{child.name}.py").is_file():
            systems.append(child.name)
    return systems


def normalize_field(value: str) -> str:
    return " ".join(value.replace(",", " ").split())


def parse_pipe_rows(path: Path) -> list[list[str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append([field.strip() for field in line.split("|") if field.strip()])
    return rows


def required_row_size(row: list[str], size: int, path: Path) -> None:
    if len(row) < size:
        raise ValueError(f"{path}: expected at least {size} pipe-delimited fields, found {len(row)}")


def old_geometry_record(row: list[str]) -> dict[str, str]:
    return {
        "name": normalize_field(row[0]),
        "mother": normalize_field(row[1]),
        "description": normalize_field(row[2]),
        "position": normalize_field(row[3]),
        "rotation": normalize_field(row[4]),
        "solid": normalize_field(row[6]),
        "dimensions": normalize_field(row[7]),
        "material": normalize_field(row[8]),
    }


def new_geometry_record(row: list[str]) -> dict[str, str]:
    return {
        "name": normalize_field(row[0]),
        "mother": normalize_field(row[4]),
        "description": normalize_field(row[19]),
        "position": normalize_field(row[5]),
        "rotation": normalize_field(row[6]),
        "solid": normalize_field(row[1]),
        "dimensions": normalize_field(row[2]),
        "material": normalize_field(row[3]),
    }


def semantic_records(path: Path, schema: str) -> dict[str, dict[str, str]]:
    records = {}
    for row in parse_pipe_rows(path):
        if schema == "clas12tags":
            required_row_size(row, 9, path)
            record = old_geometry_record(row)
        else:
            required_row_size(row, 20, path)
            record = new_geometry_record(row)
        records[record["name"]] = record
    return records


def semantic_differences(
    generated: dict[str, dict[str, str]],
    reference: dict[str, dict[str, str]],
) -> list[str]:
    differences = []

    for name in sorted(set(reference) - set(generated)):
        differences.append(f"{name}: missing generated volume")

    for name in sorted(set(generated) - set(reference)):
        differences.append(f"{name}: extra generated volume")

    for name in sorted(set(reference) & set(generated)):
        for field in GEOMETRY_FIELDS:
            reference_value = reference[name][field]
            generated_value = generated[name][field]
            if reference_value != generated_value:
                differences.append(
                    f"{name}.{field}: reference <{reference_value}> generated <{generated_value}>"
                )

    return differences


def run_system(system: str, args: argparse.Namespace, output_dir: Path) -> Path:
    system_dir = GEOMETRY_SRC / system
    script = system_dir / f"{system}.py"
    if not script.is_file():
        raise FileNotFoundError(f"Local system script not found: {script}")

    system_output_dir = output_dir / system
    system_output_dir.mkdir(parents=True, exist_ok=True)

    command = [str(args.python), str(script), "-f", "ascii", "-v", args.variation]
    if args.run is not None:
        command.extend(["-r", str(args.run)])

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    subprocess.run(command, cwd=system_output_dir, env=env, check=True)

    generated = system_output_dir / f"{system}__geometry_{args.variation}.txt"
    if not generated.is_file():
        raise FileNotFoundError(f"Expected generated geometry file was not produced: {generated}")
    return generated


def reference_file(system: str, args: argparse.Namespace) -> Path:
    variation = args.reference_variation or args.variation
    return args.clas12tags / system / f"{system}__geometry_{variation}.txt"


def compare_system(system: str, args: argparse.Namespace, output_dir: Path) -> tuple[bool, str]:
    generated = run_system(system, args, output_dir)
    reference = reference_file(system, args)
    if not reference.is_file():
        return False, f"{system}: missing reference {reference}"

    generated_records = semantic_records(generated, "pygemc")
    reference_records = semantic_records(reference, "clas12tags")
    differences = semantic_differences(generated_records, reference_records)

    if not differences:
        return True, f"{system}: ok ({len(generated_records)} geometry rows)"

    message = (
        f"{system}: differs "
        f"({len(generated_records)} generated rows, {len(reference_records)} reference rows)"
    )
    if args.diff:
        message += "\n" + "\n".join(differences)
    return False, message


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    systems = args.systems or discover_systems()
    if not systems:
        parser.error("No local geometry systems found.")

    if not args.clas12tags.is_dir():
        parser.error(f"clas12Tags geometry_source directory not found: {args.clas12tags}")

    if not args.python.is_file():
        parser.error(f"Python executable not found: {args.python}")

    cleanup = False
    if args.workdir:
        output_dir = args.workdir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = Path(tempfile.mkdtemp(prefix="clas12-geometry-compare-"))
        cleanup = not args.keep

    failures = []
    try:
        print(f"Comparing systems: {', '.join(systems)}")
        print(f"Generated ASCII workdir: {output_dir}")
        print(f"clas12Tags reference: {args.clas12tags}")
        for system in systems:
            try:
                ok, message = compare_system(system, args, output_dir)
            except subprocess.CalledProcessError as error:
                ok = False
                message = f"{system}: generation failed with exit code {error.returncode}"
            except Exception as error:  # noqa: BLE001 - report all system comparison failures.
                ok = False
                message = f"{system}: {error}"

            print(message)
            if not ok:
                failures.append(system)
    finally:
        if cleanup:
            shutil.rmtree(output_dir)

    if failures:
        sys.stdout.flush()
        print(f"Geometry comparison failed for: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
