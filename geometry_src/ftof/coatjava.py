"""coatjava bridge and volume table parser for the FTOF geometry.

The Java factory writes a temporary pipe-delimited table describing the FTOF
volumes. This module runs that factory, normalizes the text values to GEMC3
conventions, and returns typed rows to the Python geometry builder.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import subprocess
import zipfile


# FTOFGeant4Factory emits coatjava short solid names; GEMC3 expects the Geant4 names.
SOLID_NAME_MAP = {
    "Box": "G4Box",
    "Trd": "G4Trd",
    "Tube": "G4Tubs",
}


@dataclass(frozen=True)
class CoatjavaVolume:
    """One parsed row from the coatjava FTOF volume table."""

    name: str
    mother: str
    position: str
    rotation: str
    solid: str
    dimensions: str


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


def normalize_solid(value):
    """Map coatjava solid names (Box, Trd, ...) to the GEMC3 Geant4 solid names."""
    return SOLID_NAME_MAP.get(value, value)


def java_command():
    """Return a usable Java command, preferring real JDK installs over macOS stubs."""

    def usable(java):
        """Return True when the candidate binary can run `java -version`."""
        if not java:
            return False
        return subprocess.run([java, "-version"], check=False, capture_output=True).returncode == 0

    # Respect explicit Java setup first; CI and local builds may set JAVA_HOME.
    java_home = os.environ.get("JAVA_HOME")
    if java_home:
        java = Path(java_home) / "bin" / "java"
        if java.is_file() and usable(str(java)):
            return str(java)

    # Prefer common Homebrew JDK locations over /usr/bin/java, which can be a macOS launcher stub.
    for java_home in ("/opt/homebrew/opt/java", "/usr/local/opt/java"):
        java = Path(java_home) / "bin" / "java"
        if java.is_file() and usable(str(java)):
            return str(java)

    # /usr/libexec/java_home reports an installed JDK path on macOS when one exists.
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


def compiled_factory_dir(detector_dir):
    """Return a compiled CoatjavaFactory class directory when one is available."""
    if compiled_factory := os.environ.get("COATJAVA_FACTORY_CLASSES"):
        if (Path(compiled_factory) / "CoatjavaFactory.class").is_file():
            return compiled_factory

    default_build_dir = Path(detector_dir).parent.parent / "build"
    if (default_build_dir / "CoatjavaFactory.class").is_file():
        return str(default_build_dir)

    return None


def coatjava_classpath(detector_dir):
    """Return the coatjava classpath after checking that its installation is complete."""
    coatjava_dir = Path(detector_dir).parent / "coatjava"
    clas_lib_dir = coatjava_dir / "lib" / "clas"
    required_class = "org/jlab/detector/calib/utils/DatabaseConstantProvider.class"
    for jar in clas_lib_dir.glob("coat-libs-*.jar"):
        try:
            with zipfile.ZipFile(jar) as archive:
                archive.getinfo(required_class)
        except (KeyError, OSError, zipfile.BadZipFile):
            continue
        break
    else:
        raise RuntimeError(
            f"coatjava is missing or incomplete at {coatjava_dir}.\n"
            "From the clas12-systems repository root, reinstall it with:\n"
            "  ./geometry_src/install_coatjava.sh -r -l"
        )

    return os.pathsep.join(
        [
            str(clas_lib_dir / "*"),
            str(coatjava_dir / "lib" / "services" / "*"),
            str(coatjava_dir / "lib" / "utils" / "*"),
        ]
    )


def run_factory(ftof_dir, variation, run_number):
    """Run the local coatjava factory and return the generated volume table path."""
    ftof_path = Path(ftof_dir)
    output = ftof_path / f"ftof__volumes_{variation}.txt"
    classpath = coatjava_classpath(ftof_path)
    compiled_factory = compiled_factory_dir(ftof_path)
    if compiled_factory:
        command = [java_command(), "-cp", classpath + os.pathsep + compiled_factory, "CoatjavaFactory"]
    else:
        factory_source = str(ftof_path.parent / "coatjava_factories" / "CoatjavaFactory.java")
        command = [java_command(), "-cp", classpath, factory_source]

    command.extend(["--system", "ftof", "--variation", variation, "--runnumber", str(run_number)])
    subprocess.run(command, cwd=ftof_path, check=True)
    return output


def read_volumes(path):
    """Read a coatjava pipe-delimited volume table into CoatjavaVolume rows."""
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
                    solid=normalize_solid(fields[4]),
                    dimensions=comma_separate_quantities(fields[5]),
                )
            )
    return volumes


def generate_volumes(ftof_dir, variation, run_number):
    """Run coatjava, parse the generated volume table, and remove the temporary file."""
    volume_table = run_factory(ftof_dir, variation, run_number)
    volumes = read_volumes(volume_table)
    volume_table.unlink()
    return volumes
