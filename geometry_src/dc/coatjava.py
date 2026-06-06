"""coatjava bridge and volume table parser for the DC geometry."""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
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


def java_command():
    """Return a usable Java command, preferring real JDK installs over macOS stubs."""
    def usable(java):
        if not java:
            return False
        return subprocess.run([java, "-version"], check=False, capture_output=True).returncode == 0

    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java = Path(java_home) / "bin" / "java"
        if java.is_file() and usable(str(java)):
            return str(java)

    for java_home in ("/opt/homebrew/opt/java", "/usr/local/opt/java"):
        java = Path(java_home) / "bin" / "java"
        if java.is_file() and usable(str(java)):
            return str(java)

    if shutil.which("/usr/libexec/java_home"):
        result = subprocess.run(
            ["/usr/libexec/java_home"],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            java = Path(result.stdout.strip()) / "bin" / "java"
            if java.is_file() and usable(str(java)):
                return str(java)

    java = shutil.which("java")
    if usable(java):
        return java

    raise RuntimeError("Java is required to run coatjava geometry factories, but no usable JDK was found.")


def run_factory(dc_dir, variation, run_number):
    """Run the local coatjava factory and return the generated volume table path."""
    dc_path = Path(dc_dir)
    output = dc_path / f"dc__volumes_{variation}.txt"
    coatjava_dir = dc_path.parent / "coatjava"
    classpath = os.pathsep.join(
        [
            str(coatjava_dir / "lib" / "clas" / "*"),
            str(coatjava_dir / "lib" / "services" / "*"),
            str(coatjava_dir / "lib" / "utils" / "*"),
        ]
    )
    command = [
        java_command(),
        "-cp",
        classpath,
        str(dc_path.parent / "coatjava_factories" / "CoatjavaFactory.java"),
        "--system",
        "dc",
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
