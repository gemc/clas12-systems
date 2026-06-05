"""coatjava bridge and volume table parser for the DC geometry."""

from dataclasses import dataclass
from pathlib import Path
import subprocess


@dataclass(frozen=True)
class CoatjavaVolume:
    name: str
    mother: str
    position: str
    rotation: str
    solid: str
    dimensions: str
    identifiers: tuple[int, ...]


def comma_separate_quantities(value):
    """Convert coatjava whitespace-delimited quantities to GEMC3 comma-delimited strings."""
    return ", ".join(value.split())


def normalize_rotation(value):
    """Convert coatjava ordered rotations to GEMC3 comma-delimited ordered rotations."""
    fields = value.split()
    if len(fields) == 5 and fields[0] == "ordered:":
        order = fields[1]
        return ", ".join([f"ordered: {order}", *fields[2:]])
    return comma_separate_quantities(value)


def run_factory(dc_dir, variation, run_number):
    """Run the local Groovy factory and return the generated volume table path."""
    dc_path = Path(dc_dir)
    output = dc_path / f"dc__volumes_{variation}.txt"
    command = [
        "groovy",
        "-cp",
        "../*:..",
        "factory.groovy",
        "--variation",
        variation,
        "--runnumber",
        str(run_number),
    ]
    subprocess.run(command, cwd=dc_path, check=True)
    return output


def read_volumes(path):
    volumes = []
    with Path(path).open(encoding="utf-8") as volume_file:
        for line_number, line in enumerate(volume_file, start=1):
            stripped = line.strip()
            if not stripped:
                continue

            fields = [field.strip() for field in stripped.split("|")]
            if len(fields) != 7:
                raise ValueError(f"{path}:{line_number}: expected 7 pipe-delimited fields")

            volumes.append(
                CoatjavaVolume(
                    name=fields[0],
                    mother=fields[1],
                    position=comma_separate_quantities(fields[2]),
                    rotation=normalize_rotation(fields[3]),
                    solid=fields[4],
                    dimensions=comma_separate_quantities(fields[5]),
                    identifiers=tuple(int(field) for field in fields[6].split()),
                )
            )
    return volumes


def generate_volumes(dc_dir, variation, run_number):
    volume_table = run_factory(dc_dir, variation, run_number)
    volumes = read_volumes(volume_table)
    volume_table.unlink()
    return volumes
