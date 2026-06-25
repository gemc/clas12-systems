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
DEFAULT_CLAS12_EXPERIMENT = REPO_ROOT.parent / "clas12Tags" / "experiments" / "clas12"
EXCLUDED_SYSTEM_DIRS = {"coatjava", "coatjava_src", "coatjava_factories"}
GEOMETRY_FIELDS = (
    "name",
    "mother",
    "position",
    "rotation",
    "solid",
    "dimensions",
    "material",
    "digitization",
    "identifier",
)
# Values used by either schema to mean "no digitization / no identifier".
EMPTY_TOKENS = {"", "no", "none", "null"}
# GEMC2 (clas12Tags) names solids by a short alias; pygemc emits the Geant4 class name.
# Map the GEMC2 aliases onto their Geant4 classes so the two schemas compare equal.
# Aliases taken from clas12Tags source/detector/detector.cc. Names already carrying the
# ``G4`` prefix (e.g. ``G4Trap``) pass through unchanged.
SOLID_NAME_MAP = {
    "Box": "G4Box",
    "Parallelepiped": "G4Para",
    "Sphere": "G4Sphere",
    "Ellipsoid": "G4Ellipsoid",
    "Paraboloid": "G4Paraboloid",
    "Hype": "G4Hype",
    "Tube": "G4Tubs",
    "CTube": "G4CutTubs",
    "EllipticalTube": "G4EllipticalTube",
    "Eltu": "G4EllipticalTube",
    "Cons": "G4Cons",
    "Torus": "G4Torus",
    "Trd": "G4Trd",
    "Pgon": "G4Polyhedra",
    "Polycone": "G4Polycone",
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate ASCII geometry for local systems and compare it with clas12Tags references.",
    )
    parser.add_argument(
        "systems",
        nargs="*",
        help="Systems to compare. Defaults to every geometry_src/<system>/<system>.py found.",
    )
    parser.add_argument(
        "--clas12tags",
        type=Path,
        default=DEFAULT_CLAS12_EXPERIMENT,
        help=f"clas12Tags experiments/clas12 directory. Default: {DEFAULT_CLAS12_EXPERIMENT}",
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


def normalize_solid(value: str) -> str:
    """Canonicalize a solid type name to its Geant4 class name.

    GEMC2 uses short aliases ("Box", "Trd", ...) while pygemc emits the Geant4 class
    ("G4Box", "G4Trd", ...). Map aliases through :data:`SOLID_NAME_MAP`; anything already
    using a Geant4 name (or unknown) is returned unchanged.
    """
    text = normalize_field(value)
    return SOLID_NAME_MAP.get(text, text)


def normalize_digitization(value: str) -> str:
    """Canonicalize a digitization/sensitivity name; empty markers map to "".

    clas12Tags stores the digitization plugin in the ``sensitivity`` column ("no" when absent);
    pygemc stores it in the ``digitization`` column ("NULL" when ``None``).
    """
    text = value.strip()
    if text.lower() in EMPTY_TOKENS:
        return ""
    return text


def normalize_identifier(value: str, schema: str) -> str:
    """Expand an identifier string into a canonical ``name=value`` sequence.

    The two schemas serialize identifiers differently:
      * clas12tags: space-separated triplets ``name manual value`` (the rule word is dropped).
      * pygemc: ``set_identifier`` output ``name: value, name: value`` (comma-separated pairs).

    Both collapse to ``name=value name=value`` so they can be compared directly. Empty markers
    ("no"/"none"/"null") map to "". Unexpected layouts fall back to the normalized raw string.
    """
    text = value.strip()
    if text.lower() in EMPTY_TOKENS:
        return ""

    pairs: list[tuple[str, str]] = []
    if schema == "clas12tags":
        tokens = text.split()
        if len(tokens) % 3 != 0:
            return normalize_field(text)
        for index in range(0, len(tokens), 3):
            pairs.append((tokens[index], tokens[index + 2]))
    else:
        for chunk in text.split(","):
            chunk = chunk.strip()
            if not chunk:
                continue
            if ":" not in chunk:
                return normalize_field(text)
            name, tag = chunk.split(":", 1)
            pairs.append((name.strip(), tag.strip()))

    return " ".join(f"{name}={tag}" for name, tag in pairs)


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
        "solid": normalize_solid(row[6]),
        "dimensions": normalize_field(row[7]),
        "material": normalize_field(row[8]),
        "digitization": normalize_digitization(row[15]),
        "identifier": normalize_identifier(row[17], "clas12tags"),
    }


def new_geometry_record(row: list[str]) -> dict[str, str]:
    return {
        "name": normalize_field(row[0]),
        "mother": normalize_field(row[4]),
        "description": normalize_field(row[19]),
        "position": normalize_field(row[5]),
        "rotation": normalize_field(row[6]),
        "solid": normalize_solid(row[1]),
        "dimensions": normalize_field(row[2]),
        "material": normalize_field(row[3]),
        "digitization": normalize_digitization(row[13]),
        "identifier": normalize_identifier(row[14], "pygemc"),
    }


def semantic_records(path: Path, schema: str) -> dict[str, dict[str, str]]:
    records = {}
    for row in parse_pipe_rows(path):
        if schema == "clas12tags":
            required_row_size(row, 18, path)
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

    command = [str(args.python), str(script), "-f", "ascii"]

    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    python_path = [str(GEOMETRY_SRC)]
    if env.get("PYTHONPATH"):
        python_path.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(python_path)

    subprocess.run(command, cwd=system_output_dir, env=env, check=True)
    return system_output_dir


def variation_files(directory: Path, system: str) -> dict[str, Path]:
    files = {}
    prefix = f"{system}__geometry_"
    suffix = ".txt"
    for path in sorted(directory.glob(f"{prefix}*{suffix}")):
        variation = path.name[len(prefix) : -len(suffix)]
        files[variation] = path
    return files


def compare_variation(
    system: str,
    variation: str,
    generated: Path,
    reference: Path,
) -> tuple[bool, str]:
    generated_records = semantic_records(generated, "pygemc")
    reference_records = semantic_records(reference, "clas12tags")
    differences = semantic_differences(generated_records, reference_records)

    if not differences:
        return True, f"{system}/{variation}: ok ({len(generated_records)} geometry rows)"

    message = (
        f"{system}/{variation}: differs "
        f"({len(generated_records)} generated rows, {len(reference_records)} reference rows)"
    )
    message += "\n" + "\n".join(differences)
    return False, message


def compare_system(system: str, args: argparse.Namespace, output_dir: Path) -> tuple[bool, list[str]]:
    generated_dir = run_system(system, args, output_dir)
    reference_dir = args.clas12tags / system
    if not reference_dir.is_dir():
        return False, [f"{system}: missing reference directory {reference_dir}"]

    generated_files = variation_files(generated_dir, system)
    reference_files = variation_files(reference_dir, system)
    generated_variations = set(generated_files)
    reference_variations = set(reference_files)

    messages = []
    if generated_variations != reference_variations:
        missing = sorted(reference_variations - generated_variations)
        extra = sorted(generated_variations - reference_variations)
        if missing:
            messages.append(f"{system}: missing generated variations: {', '.join(missing)}")
        if extra:
            messages.append(f"{system}: extra generated variations: {', '.join(extra)}")
        return False, messages

    ok = True
    for variation in sorted(generated_variations):
        variation_ok, message = compare_variation(
            system,
            variation,
            generated_files[variation],
            reference_files[variation],
        )
        messages.append(message)
        ok = ok and variation_ok
    return ok, messages


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    systems = args.systems or discover_systems()
    if not systems:
        parser.error("No local geometry systems found.")

    if not args.clas12tags.is_dir():
        parser.error(f"clas12Tags experiments/clas12 directory not found: {args.clas12tags}")

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
        print(f"clas12Tags experiments/clas12 reference: {args.clas12tags}")
        for system in systems:
            try:
                ok, messages = compare_system(system, args, output_dir)
            except subprocess.CalledProcessError as error:
                ok = False
                messages = [f"{system}: generation failed with exit code {error.returncode}"]
            except Exception as error:  # noqa: BLE001 - report all system comparison failures.
                ok = False
                messages = [f"{system}: {error}"]

            for message in messages:
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
