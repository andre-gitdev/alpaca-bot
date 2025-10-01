"""Bootstrap helpers for ensuring Python dependencies are installed."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

import pkg_resources

path_to_reqs = '/workspaces/alpaca-bot/folder/requirements.txt' #Update if necessary

def read_requirements(path: Path) -> List[str]:
    """Return all requirement specifiers from ``requirements.txt``."""
    requirements: List[str] = []
    for line in path.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        requirements.append(stripped)
    return requirements


def find_missing(requirements: Iterable[str]) -> List[str]:
    """Return requirement strings that are not satisfied in the current env."""
    missing: List[str] = []
    for requirement in requirements:
        try:
            pkg_resources.require(requirement)
        except pkg_resources.DistributionNotFound:
            missing.append(requirement)
        except pkg_resources.VersionConflict:
            missing.append(requirement)
    return missing


def install(requirements: Iterable[str]) -> None:
    """Install the provided requirement specifiers via ``pip``."""
    command = [sys.executable, "-m", "pip", "install", *requirements]
    subprocess.check_call(command)


def ensure_requirements(requirements_path: Path | str = path_to_reqs, *, auto_install: bool = True) -> None:
    """Ensure that all requirements are present before running demos.

    Parameters
    ----------
    requirements_path:
        Path to the requirements file to inspect. Defaults to ``requirements.txt``.
    auto_install:
        When True (the default) missing requirements are installed automatically.
        When False a helpful error is raised listing the missing dependencies.
    """

    path = Path(requirements_path)
    if not path.exists():
        raise FileNotFoundError(f"Could not locate requirements file at {path!s}")

    requirements = read_requirements(path)
    missing = find_missing(requirements)

    if not missing:
        return

    if not auto_install:
        formatted = "\n".join(f"  - {req}" for req in missing)
        raise RuntimeError(
            "Missing Python packages detected. Install them with:\n"
            f"  pip install -r {path}\n\nMissing entries:\n{formatted}"
        )

    install(missing)


def main() -> None:
    ensure_requirements()


if __name__ == "__main__":
    main()
