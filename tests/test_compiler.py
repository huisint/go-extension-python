# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import doctest
import shutil
import os

from go_extension import (
    compiler,
    exceptions,
    extension,
)
from tests import utils


class TestGopyCompiler___init__(TestCase):
    go_module_name: str = "github.com/huisint/go-extension-python"

    def test_go_command(self) -> None:
        assert compiler.GoPyCompiler.go_command == "go"
        go_compiler = compiler.GoPyCompiler(go_command="gogo")
        self.assertEqual(go_compiler.go_command, "gogo")

    def test_verbose(self) -> None:
        assert compiler.GoPyCompiler.verbose is False
        go_compiler = compiler.GoPyCompiler(verbose=True)
        self.assertTrue(go_compiler.verbose)

    def test_dry_run(self) -> None:
        assert compiler.GoPyCompiler.dry_run is False
        go_compiler = compiler.GoPyCompiler(dry_run=True)
        self.assertTrue(go_compiler.dry_run)

    def test_force(self) -> None:
        assert compiler.GoPyCompiler.force is False
        go_compiler = compiler.GoPyCompiler(force=True)
        self.assertTrue(go_compiler.force)

    def test_inplace(self) -> None:
        assert compiler.GoPyCompiler.force is False
        complr = compiler.GoPyCompiler(inplace=True)
        self.assertTrue(complr.inplace)

    def test_env(self) -> None:
        assert compiler.GoPyCompiler.env.get("LD_LIBRATY_PATH", None) is None
        go_compiler = compiler.GoPyCompiler()
        self.assertTrue(hasattr(go_compiler, "env"))
        self.assertIsNotNone(go_compiler.env.get("LD_LIBRATY_PATH", None))


@mock.patch("go_extension.compiler._goimports_is_installed")
@mock.patch("go_extension.compiler._gopy_is_installed")
class TestGoPyCompiler_install_build_tools(TestCase):
    def test_all_installed(
        self,
        gopy_is_installed_mock: mock.Mock,
        goimports_is_installed_mock: mock.Mock,
    ) -> None:
        gopy_is_installed_mock.return_value = True
        goimports_is_installed_mock.return_value = True
        go_compiler = compiler.GoPyCompiler()
        go_compiler.install_build_tools()
        self.assertIsNotNone(shutil.which(go_compiler.go_command))
        try:
            gopy_is_installed_mock.assert_called_once()
            goimports_is_installed_mock.assert_called_once()
        except Exception as err:
            self.fail(err)

    def test_go_command_not_exist(
        self,
        gopy_is_installed_mock: mock.Mock,
        goimports_is_installed_mock: mock.Mock,
    ) -> None:
        unexist_go_command = "unexist_go"
        assert shutil.which(unexist_go_command) is None
        go_compiler = compiler.GoPyCompiler(go_command=unexist_go_command)
        with self.assertRaises(exceptions.GoNotFoundError):
            go_compiler.install_build_tools()

    def test_install_gopy(
        self,
        gopy_is_installed_mock: mock.Mock,
        goimports_is_installed_mock: mock.Mock,
    ) -> None:
        gopy_is_installed_mock.return_value = False
        go_compiler = compiler.GoPyCompiler()
        go_compiler.install_build_tools()
        self.assertIsNotNone(shutil.which("gopy"))
        gopy_is_installed_mock.assert_called_once()

    def test_install_goimports(
        self,
        gopy_is_installed_mock: mock.Mock,
        goimports_is_installed_mock: mock.Mock,
    ) -> None:
        goimports_is_installed_mock.return_value = False
        go_compiler = compiler.GoPyCompiler()
        go_compiler.install_build_tools()
        self.assertIsNotNone(shutil.which("goimports"))
        goimports_is_installed_mock.assert_called_once()


class TestGoPyCompiler_generate(TestCase):
    go_module_name: str = "github.com/huisint/go-extension-python"

    def setUp(self) -> None:
        self.compiler = compiler.GoPyCompiler()

    def test_one_source(self) -> None:
        pkg = "tests/go_src"
        utils.create_go_pkg(pkg)
        ext = extension.GoExtension("tests.go", [self.go_module_name + "/" + pkg])
        output = "tests/go_gen"
        try:
            self.compiler.generate(ext, output)
            self.assertTrue(os.path.exists(output))
        finally:
            shutil.rmtree(output, ignore_errors=True)
            utils.clean_up_go_pkg(pkg)

    def test_two_go_sources(self) -> None:
        pkgs = ["tests/go_src", "tests/go_src2"]
        ext = extension.GoExtension(
            "tests.go",
            [self.go_module_name + "/" + pkg for pkg in pkgs],
        )
        output = "tests/go_gen_two_srcs"
        for pkg in pkgs:
            utils.create_go_pkg(pkg)
        try:
            self.compiler.generate(ext, output)
            self.assertTrue(os.path.exists(output))
        finally:
            shutil.rmtree(output, ignore_errors=True)
            for pkg in pkgs:
                utils.clean_up_go_pkg(pkg)


class TestGoPyCompiler_build(TestCase):
    go_module_name: str = "github.com/huisint/go-extension-python"

    def setUp(self) -> None:
        self.compiler = compiler.GoPyCompiler()

    def test_one_source(self) -> None:
        pkg = "tests/go_src"
        ext = extension.GoExtension("tests.go", [self.go_module_name + "/" + pkg])
        output = "tests/go_build"
        utils.create_go_pkg(pkg)
        try:
            self.compiler.build(ext, output)
            self.assertTrue(os.path.exists(output))
        finally:
            shutil.rmtree(output, ignore_errors=True)
            utils.clean_up_go_pkg(pkg)

    def test_two_go_sources(self) -> None:
        pkgs = ["tests/go_src", "tests/go_src2"]
        ext = extension.GoExtension(
            "tests.go",
            [self.go_module_name + "/" + pkg for pkg in pkgs],
        )
        output = "tests/go_build_two_srcs"
        for pkg in pkgs:
            utils.create_go_pkg(pkg)
        try:
            self.compiler.build(ext, output)
            self.assertTrue(os.path.exists(output))
        finally:
            shutil.rmtree(output, ignore_errors=True)
            for pkg in pkgs:
                utils.clean_up_go_pkg(pkg)


def load_tests(loader, tests, _):  # type: ignore
    tests.addTests(doctest.DocTestSuite(compiler))
    return tests
