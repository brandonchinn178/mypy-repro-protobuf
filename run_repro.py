#!/usr/bin/env python3

from __future__ import annotations

import abc
import argparse
import dataclasses
import enum
import logging
import os
import shlex
import shutil
import subprocess
import venv as venv_impl
from pathlib import Path

HERE = Path(__file__).absolute().parent
VENVS_DIR = HERE / "venvs"

MYPY_DEP = "mypy==1.18.1"
PROTOBUF_DEP = "protobuf"
TYPES_PROTOBUF_DEP = "types-protobuf"

class Scenario(enum.Enum):
    VENV_1 = "venv-1"
    VENV_2 = "venv-2"
    VENV_3 = "venv-3"

def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format=">>> %(message)s",
    )

    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=[s.value for s in Scenario])
    args = parser.parse_args()

    scenario = Scenario(args.scenario)

    mypy_venv: Venv
    match scenario:
        case Scenario.VENV_1:
            mypy_venv = Venv.get_or_create(scenario.value)
            mypy_venv.install(MYPY_DEP, PROTOBUF_DEP, TYPES_PROTOBUF_DEP)
        case Scenario.VENV_2:
            mypy_venv = Venv.get_or_create("mypy")
            mypy_venv.install(MYPY_DEP)
            venv = Venv.get_or_create(scenario.value)
            venv.install(PROTOBUF_DEP, TYPES_PROTOBUF_DEP)
            set_pythonpath(venv.get_site_packages())
        case Scenario.VENV_3:
            mypy_venv = Venv.get_or_create("mypy")
            mypy_venv.install(MYPY_DEP)
            protobuf_venv = Venv.get_or_create(scenario.value)
            protobuf_venv.install(PROTOBUF_DEP)
            types_protobuf_venv = Venv.get_or_create(f"{scenario.value}-stubs")
            types_protobuf_venv.install(TYPES_PROTOBUF_DEP)
            set_pythonpath(
                protobuf_venv.get_site_packages(),
                types_protobuf_venv.get_site_packages(),
            )

    cmd = [
        mypy_venv.path / "bin" / "mypy",
        "--cache-dir=/dev/null",
        HERE / "main.py",
    ]
    logging.info(f"Running: {shlex.join(map(str, cmd))}")
    os.execv(cmd[0], cmd)

@dataclasses.dataclass(frozen=True)
class Venv:
    path: Path

    @classmethod
    def get_or_create(cls, name: str) -> Venv:
        path = VENVS_DIR / name
        if not path.exists():
            logging.info(f"Creating venv at {path}...")
            venv_impl.create(path, with_pip=True)
        return cls(path=path)

    def install(self, *deps: str) -> None:
        logging.info(f"Installing in {self.path}: {deps}")
        subprocess.run([self.path / "bin" / "pip", "install", "-q", *deps], check=True)

    def get_site_packages(self) -> Path:
        return next(self.path.glob("lib/python*/site-packages"))

def set_pythonpath(*dirs: Path) -> None:
    python_path = ":".join(d.as_posix() for d in dirs)
    logging.info(f"Set PYTHONPATH={python_path}")
    os.environ["PYTHONPATH"] = python_path

if __name__ == "__main__":
    main()
