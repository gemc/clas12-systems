#!/usr/bin/env python3
"""Install pygemc and its dependencies into the prefix, matching GEMC's Python environment layout."""

import os
from pathlib import Path
import subprocess
import sys


def main() -> None:
    if os.environ.get('GEMC_SKIP_PYTHON_ENV_INSTALL') == '1':
        print(' > Skipping Python environment installation (GEMC_SKIP_PYTHON_ENV_INSTALL=1)')
        return

    prefix = Path(os.environ.get('MESON_INSTALL_DESTDIR_PREFIX', os.environ['MESON_INSTALL_PREFIX']))
    pygemc_src = sys.argv[1]
    venv_dir = prefix / 'python_env'
    venv_python = str(venv_dir / 'bin' / 'python3')

    if venv_dir.exists():
        print(f' > Python environment already exists at {venv_dir}, updating pygemc')
    else:
        print(f' > Installing Python environment at {venv_dir}')
        subprocess.run([sys.executable, '-m', 'venv', str(venv_dir)], check=True)
        subprocess.run(
            [venv_python, '-m', 'pip', 'install', '--upgrade', 'pip', 'setuptools', 'wheel'], check=True,
        )

    subprocess.run([venv_python, '-m', 'pip', 'install', pygemc_src], check=True)


if __name__ == '__main__':
    main()
