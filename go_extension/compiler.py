# Copyright (c) 2021 Shuhei Nitta. All rights reserved.

import os
import sys
import shutil
from pip._internal import metadata
from pip._vendor.packaging import utils
from setuptools._distutils import spawn, log

from go_extension import extension, exceptions


class GoPyCompiler:
    """
    Wrapper class of command `gopy`

    See also
    --------
    https://github.com/go-python/gopy

    """

    go_command: str = "go"
    verbose: bool = False
    dry_run: bool = False
    force: bool = False
    inplace: bool = False
    env: dict[str, str] = dict()

    def __init__(
        self,
        go_command: str = "go",
        verbose: bool = False,
        dry_run: bool = False,
        force: bool = False,
        inplace: bool = False,
    ) -> None:
        """
        Parameters
        ----------
        go_command : str
            Path to go executable command. used as `go mod`, `go get`, etc...

        other parameters : bool
            See distutils.ccompiler.CCompiler.__init__().

        """
        self.go_command = go_command
        self.verbose = verbose
        self.dry_run = dry_run
        self.force = force
        self.inplace = inplace
        self.env = os.environ.copy()
        self.env["LD_LIBRATY_PATH"] = (self.env.get("LD_LIBRATY_PATH", "") + ":" + os.curdir).strip(":")

    def install_build_tools(self) -> None:
        """
        Install gopy, goimports, and pybindgen.

        Raises
        ------
        go_extension.exceptions.GoNotFoundError
            If `go` command not found.
        """
        if not shutil.which(self.go_command):
            # ToDo: should check go version
            raise exceptions.GoNotFoundError("Go1.16 or above is required to build this extension.")

        if not _gopy_is_installed():
            log.info("Installing gopy...")
            cmd = [
                self.go_command,
                "install",
                "github.com/go-python/gopy@latest"
            ]
            self.spawn(cmd)

        if not _goimports_is_installed():
            log.info("Installing goimports...")
            cmd = [
                self.go_command,
                "install",
                "golang.org/x/tools/cmd/goimports@latest",
            ]
            self.spawn(cmd)

        if not _pybindgen_is_installed():
            pybindgen = "pybindgen"
            log.info(f"Installing {pybindgen}...")
            cmd = [sys.executable, "-m", "pip", "install", "-Uq", pybindgen]
            self.spawn(cmd)

    def generate(self, ext: extension.GoExtension, output: str | os.PathLike[str]) -> None:
        """
        Generate (C)Python language bindings for Go.

        Parameters
        ----------
        ext : go_extension.extension.GoExtension
            Go extension.

        output : str | os.PathLike[str]
            Output directory for bindings.

        See also
        --------
        https://github.com/go-python/gopy

        """
        self.install_build_tools()
        cmd: list[str] = [
            "gopy",
            "gen",
            f"-name={ext._compiled_name}",
            "-no-make",
            "-rename",
            f"-vm={sys.executable}",
            f"-output={output}",
        ] + ext.packages
        self.spawn(cmd)

    def build(self, ext: extension.GoExtension, output: str | os.PathLike[str]) -> None:
        """
        Generate and compile (C)Python language bindings for Go.

        Parameters
        ----------
        ext : go_extension.extension.GoExtension
            Go extension.

        output : str | os.PathLike[str]
            Output directory for bindings.

        See also
        --------
        https://github.com/go-python/gopy
        """
        self.install_build_tools()
        cmd: list[str] = [
            "gopy",
            "build",
            f"-name={ext._compiled_name}",
            "-no-make",
            "-rename",
            f"-vm={sys.executable}",
            f"-output={output}",
        ] + ext.packages
        self.spawn(cmd)

    def spawn(self, cmd: list[str]) -> None:
        """
        Run another program, specified as a command list 'cmd', in a new process.

        Parameters
        ----------
        cmd : list[str]
            Argument list for the new process.
        """
        spawn.spawn(cmd, verbose=self.verbose, dry_run=self.dry_run, env=self.env)


def _gopy_is_installed() -> bool:
    return bool(shutil.which("gopy"))


def _goimports_is_installed() -> bool:
    return bool(shutil.which("goimports"))


def _pybindgen_is_installed() -> bool:
    env = metadata.get_default_environment()
    pip_installed = {dist.canonical_name: dist for dist in env._iter_distributions()}
    return bool(utils.canonicalize_name("pybindgen") in pip_installed)
