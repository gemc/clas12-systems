#!/usr/bin/env python3
"""Compare generated CLAS12 systems ASCII databases (geometry, materials) with clas12Tags references."""

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
MATERIAL_FIELDS = (
    "name",
    "density",
    "ncomponents",
    "components",
    "photonEnergy",
    "indexOfRefraction",
    "absorptionLength",
    "reflectivity",
    "efficiency",
    "fastcomponent",
    "slowcomponent",
    "scintillationyield",
    "resolutionscale",
    "fasttimeconstant",
    "slowtimeconstant",
    "yieldratio",
    "rayleigh",
    "birksConstant",
    "mie",
    "mieforward",
    "miebackward",
    "mieratio",
)
SECTIONS = ("geometry", "materials")
# Volumes that gemc3 intentionally does not generate. gemc3 stops optical photons at the
# stepping-action level, so it drops GEMC2's per-PMT light-stopper volumes. Skip them on both
# sides so the reference's stoppers are not reported as missing generated volumes.
SKIP_VOLUME_PREFIXES = {
    "ltcc": ("pmt_light_stopper_",),
}
# GEMC2 hardcodes some materials in the engine (source/materials/cpp_materials.cc); the ones
# also predefined by gemc3 (g4system/g4materials.cc) map onto their gemc3 names here.
MATERIAL_NAME_MAP = {
    "Air_Opt": "G4_AIR_Optical",
}
# Values used by either schema to mean "no digitization / no identifier / unset material property".
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
        description="Generate ASCII databases (geometry, materials) for local systems "
        "and compare them with clas12Tags references.",
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
    tokens = value.replace(",", " ").split()
    return " ".join(normalize_zero_token(token) for token in tokens)


def normalize_zero_token(token: str) -> str:
    """Map any zero-valued token to "0".

    GEMC2 prints unset positions/rotations without units ("0 0 0") while pygemc
    always carries units ("0*mm, 0*mm, 0*mm"); both collapse to "0 0 0".
    """
    magnitude = token.split("*", 1)[0]
    try:
        if float(magnitude) == 0.0:
            return "0"
    except ValueError:
        pass
    return token


def normalize_solid(value: str) -> str:
    """Canonicalize a solid type name to its Geant4 class name.

    GEMC2 uses short aliases ("Box", "Trd", ...) while pygemc emits the Geant4 class
    ("G4Box", "G4Trd", ...). Map aliases through :data:`SOLID_NAME_MAP`; anything already
    using a Geant4 name (or unknown) is returned unchanged.
    """
    text = normalize_field(value)
    return SOLID_NAME_MAP.get(text, text)


def normalize_material_name(value: str) -> str:
    """Canonicalize a volume material name to its gemc3 name.

    Materials that GEMC2 hardcodes in the engine and gemc3 predefines under a different name
    map through :data:`MATERIAL_NAME_MAP`; anything else is returned unchanged.
    """
    text = normalize_field(value)
    return MATERIAL_NAME_MAP.get(text, text)


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


def normalize_material_number_token(token: str) -> str:
    """Canonicalize a numeric token, preserving any ``*unit`` suffix.

    GEMC2 (perl) drops trailing zeros ("1.543784") while pygemc keeps the raw source string
    ("1.5437840"); both map to the shortest round-trip float representation.
    """
    magnitude, separator, unit = token.partition("*")
    try:
        number = float(magnitude)
    except ValueError:
        return token
    return repr(number) + separator + unit


def normalize_material_field(value: str) -> str:
    tokens = value.replace(",", " ").split()
    return " ".join(normalize_material_number_token(token) for token in tokens)


def normalize_material_value(value: str) -> str:
    """Canonicalize an optional material property; empty markers map to "".

    clas12Tags defaults unset optical/scintillation lists to "none" and unset scalars to "-1";
    pygemc writes "NULL" for both.
    """
    text = value.strip()
    if text.lower() in EMPTY_TOKENS or text == "-1":
        return ""
    return normalize_material_field(text)


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
        "material": normalize_material_name(row[8]),
        "digitization": normalize_digitization(row[15]),
        "identifier": normalize_identifier(row[17], "clas12tags"),
    }


def new_geometry_record(row: list[str]) -> dict[str, str]:
    # A boolean solid lives in the solidsOpr column; clas12Tags encodes it in the
    # type column as "Operation: a - b".
    solid = normalize_solid(row[1])
    dimensions = normalize_field(row[2])
    solids_opr = normalize_digitization(row[16])
    if solids_opr:
        solid = normalize_field(f"Operation: {solids_opr}")

    # A copied volume stores its source in copyOf; clas12Tags encodes it in the
    # type column as "CopyOf <source>" and prints its unused dimensions as zero.
    copy_of = normalize_digitization(row[15])
    if copy_of:
        solid = normalize_field(f"CopyOf {copy_of}")
        dimensions = "0"

    # A mirror surface lives in the mirror column; clas12Tags encodes it in the
    # sensitivity column as "mirror: <surface>".
    digitization = normalize_digitization(row[13])
    mirror = normalize_digitization(row[17])
    if not digitization and mirror:
        digitization = f"mirror: {mirror}"

    return {
        "name": normalize_field(row[0]),
        "mother": normalize_field(row[4]),
        "description": normalize_field(row[19]),
        "position": normalize_field(row[5]),
        "rotation": normalize_field(row[6]),
        "solid": solid,
        "dimensions": dimensions,
        "material": normalize_field(row[3]),
        "digitization": digitization,
        "identifier": normalize_identifier(row[14], "pygemc"),
    }


def old_material_record(row: list[str]) -> dict[str, str]:
    return {
        "name": normalize_field(row[0]),
        "description": normalize_field(row[1]),
        "density": normalize_material_field(row[2]),
        "ncomponents": normalize_field(row[3]),
        "components": normalize_material_field(row[4]),
        "photonEnergy": normalize_material_value(row[5]),
        "indexOfRefraction": normalize_material_value(row[6]),
        "absorptionLength": normalize_material_value(row[7]),
        "reflectivity": normalize_material_value(row[8]),
        "efficiency": normalize_material_value(row[9]),
        "fastcomponent": normalize_material_value(row[10]),
        "slowcomponent": normalize_material_value(row[11]),
        "scintillationyield": normalize_material_value(row[12]),
        "resolutionscale": normalize_material_value(row[13]),
        "fasttimeconstant": normalize_material_value(row[14]),
        "slowtimeconstant": normalize_material_value(row[15]),
        "yieldratio": normalize_material_value(row[16]),
        "rayleigh": normalize_material_value(row[17]),
        "birksConstant": normalize_material_value(row[18]),
        "mie": normalize_material_value(row[19]),
        "mieforward": normalize_material_value(row[20]),
        "miebackward": normalize_material_value(row[21]),
        "mieratio": normalize_material_value(row[22]),
    }


def new_material_record(row: list[str]) -> dict[str, str]:
    # pygemc does not store ncomponents; the composition string alternates
    # component name and amount, so the pair count recovers it.
    components = normalize_material_field(row[2])
    ncomponents = str(len(components.split()) // 2)

    # pygemc has no mie scattering fields; they compare as unset so any
    # reference material carrying non-default mie values is reported.
    return {
        "name": normalize_field(row[0]),
        "description": normalize_field(row[3]),
        "density": normalize_material_field(row[1]),
        "ncomponents": ncomponents,
        "components": components,
        "photonEnergy": normalize_material_value(row[4]),
        "indexOfRefraction": normalize_material_value(row[5]),
        "absorptionLength": normalize_material_value(row[6]),
        "reflectivity": normalize_material_value(row[7]),
        "efficiency": normalize_material_value(row[8]),
        "fastcomponent": normalize_material_value(row[9]),
        "slowcomponent": normalize_material_value(row[10]),
        "scintillationyield": normalize_material_value(row[11]),
        "resolutionscale": normalize_material_value(row[12]),
        "fasttimeconstant": normalize_material_value(row[13]),
        "slowtimeconstant": normalize_material_value(row[14]),
        "yieldratio": normalize_material_value(row[15]),
        "rayleigh": normalize_material_value(row[17]),
        "birksConstant": normalize_material_value(row[16]),
        "mie": "",
        "mieforward": "",
        "miebackward": "",
        "mieratio": "",
    }


def semantic_records(path: Path, schema: str, section: str) -> dict[str, dict[str, str]]:
    records = {}
    for row in parse_pipe_rows(path):
        if section == "materials":
            if schema == "clas12tags":
                required_row_size(row, 23, path)
                record = old_material_record(row)
            else:
                required_row_size(row, 18, path)
                record = new_material_record(row)
        elif schema == "clas12tags":
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
    fields: tuple[str, ...],
    kind: str,
) -> list[str]:
    differences = []

    for name in sorted(set(reference) - set(generated)):
        differences.append(f"{name}: missing generated {kind}")

    for name in sorted(set(generated) - set(reference)):
        differences.append(f"{name}: extra generated {kind}")

    for name in sorted(set(reference) & set(generated)):
        for field in fields:
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


def variation_files(directory: Path, system: str, section: str) -> dict[str, Path]:
    files = {}
    prefix = f"{system}__{section}_"
    suffix = ".txt"
    for path in sorted(directory.glob(f"{prefix}*{suffix}")):
        variation = path.name[len(prefix) : -len(suffix)]
        files[variation] = path
    return files


def drop_skipped_volumes(
    records: dict[str, dict[str, str]], system: str
) -> dict[str, dict[str, str]]:
    """Remove records whose name starts with a skipped prefix for ``system``."""
    prefixes = SKIP_VOLUME_PREFIXES.get(system)
    if not prefixes:
        return records
    return {
        name: record
        for name, record in records.items()
        if not name.startswith(prefixes)
    }


def compare_variation(
    system: str,
    variation: str,
    generated: Path,
    reference: Path,
    section: str,
) -> tuple[bool, str]:
    generated_records = drop_skipped_volumes(semantic_records(generated, "pygemc", section), system)
    reference_records = drop_skipped_volumes(semantic_records(reference, "clas12tags", section), system)
    fields = GEOMETRY_FIELDS if section == "geometry" else MATERIAL_FIELDS
    kind = "volume" if section == "geometry" else "material"
    differences = semantic_differences(generated_records, reference_records, fields, kind)

    # CI parses these per-variation lines; a passing detail must start with "ok".
    if not differences:
        return True, f"{system}/{variation}: ok ({len(generated_records)} {section} rows)"

    message = (
        f"{system}/{variation}: {section} differs "
        f"({len(generated_records)} generated rows, {len(reference_records)} reference rows)"
    )
    message += "\n" + "\n".join(differences)
    return False, message


def compare_section(
    system: str,
    section: str,
    generated_dir: Path,
    reference_dir: Path,
) -> tuple[bool, list[str]]:
    generated_files = variation_files(generated_dir, system, section)
    reference_files = variation_files(reference_dir, system, section)

    # Systems built entirely from standard Geant4 materials ship no materials files.
    if not generated_files and not reference_files:
        return True, []

    messages = []
    if set(generated_files) != set(reference_files):
        missing = sorted(set(reference_files) - set(generated_files))
        extra = sorted(set(generated_files) - set(reference_files))
        if missing:
            messages.append(f"{system}: missing generated {section} variations: {', '.join(missing)}")
        if extra:
            messages.append(f"{system}: extra generated {section} variations: {', '.join(extra)}")
        return False, messages

    ok = True
    for variation in sorted(generated_files):
        variation_ok, message = compare_variation(
            system,
            variation,
            generated_files[variation],
            reference_files[variation],
            section,
        )
        messages.append(message)
        ok = ok and variation_ok
    return ok, messages


def compare_system(system: str, args: argparse.Namespace, output_dir: Path) -> tuple[bool, list[str]]:
    generated_dir = run_system(system, args, output_dir)
    reference_dir = args.clas12tags / system
    if not reference_dir.is_dir():
        return False, [f"{system}: missing reference directory {reference_dir}"]

    ok = True
    messages = []
    for section in SECTIONS:
        section_ok, section_messages = compare_section(system, section, generated_dir, reference_dir)
        messages.extend(section_messages)
        ok = ok and section_ok
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
        print(f"ASCII database comparison failed for: {', '.join(failures)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
