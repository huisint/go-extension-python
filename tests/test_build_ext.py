# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
from unittest import TestCase, mock
import doctest
import os
import shutil
from setuptools import dist, extension as setuptools_ext

from go_extension import build_ext, extension
from tests import utils


class Testbuild_ext_build_extension(TestCase):
    def setUp(self) -> None:
        self.command = build_ext.build_ext(dist.Distribution())

    @mock.patch("go_extension.build_ext.build_ext.build_go")
    def test_GoExtension(self, build_go_mock: mock.Mock) -> None:
        ext = mock.Mock(spec=extension.GoExtension)
        self.command.build_extension(ext)
        build_go_mock.assert_called_once()

    @mock.patch("go_extension.build_ext.super")
    def test_extension_other_than_GoExtension(self, build_ext_mock: mock.Mock) -> None:
        ext = mock.Mock(spec=setuptools_ext.Extension)
        assert not isinstance(ext, extension.GoExtension)
        self.command.build_extension(ext)
        build_ext_mock.assert_called_once()


class Testbuild_ext_build_go(TestCase):
    go_module_name = "github.com/huisint/go-extension-python"
    command: build_ext.build_ext
    ext: extension.GoExtension

    def setUp(self) -> None:
        self.command = build_ext.build_ext(dist.Distribution())
        self.command.build_lib = "build/test_build_go"
        pkg = "tests/go_src"
        self.ext = extension.GoExtension("tests.go", [self.go_module_name + "/" + pkg])
        utils.create_go_pkg(pkg)

    def tearDown(self) -> None:
        pkg = "tests/go_src"
        utils.clean_up_go_pkg(pkg)
        shutil.rmtree(self.command.build_lib, ignore_errors=True)

    def test_default(self) -> None:
        self.command.build_go(self.ext)
        self.assertTrue(os.path.exists(self.command.build_lib))

    @mock.patch("go_extension.build_ext.build_ext.should_skip_ext")
    def test_skip(self, should_skip_ext_mock: mock.Mock) -> None:
        should_skip_ext_mock.return_value = True
        self.command.build_go(self.ext)
        should_skip_ext_mock.assert_called_once()

    def test_inplace(self) -> None:
        inplaced_pkg = os.path.join(*self.ext.original_name.split("."))
        self.command.gopy_compiler.inplace = True
        try:
            self.command.build_go(self.ext)
            self.assertTrue(os.path.exists(inplaced_pkg))
        finally:
            shutil.rmtree(inplaced_pkg, ignore_errors=True)


def load_tests(loader, tests, _):  # type: ignore
    tests.addTests(doctest.DocTestSuite(build_ext))
    return tests
