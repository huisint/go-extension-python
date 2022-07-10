# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
from unittest import TestCase
import os
import sys
import shutil
import setuptools

from go_extension import extension

from tests import utils


class TestIntegration(TestCase):
    pkg: str = "tests/go_src"

    def setUp(self) -> None:
        utils.create_go_pkg(self.pkg)
        self.ext = extension.GoExtension("tests.go", ["github.com/huisint/go-extension-python/" + self.pkg])

    def tearDown(self) -> None:
        utils.clean_up_go_pkg(self.pkg)

    def test_setup(self) -> None:
        build_lib = "tests/build"
        sys.argv = ["", "build_ext", "-b", build_lib]
        try:
            setuptools.setup(ext_modules=[self.ext])
            self.assertTrue(os.path.exists(build_lib))
        finally:
            shutil.rmtree(build_lib, ignore_errors=True)

    def test_setup_inplace(self) -> None:
        build_lib = "tests/build"
        sys.argv = ["", "build_ext", "-b", build_lib, "--inplace"]
        inplaced = os.path.join(*self.ext.original_name.split("."))
        try:
            setuptools.setup(ext_modules=[self.ext])
            self.assertTrue(os.path.exists(build_lib))
            self.assertTrue(os.path.exists(inplaced))
        finally:
            shutil.rmtree(build_lib, ignore_errors=True)
            shutil.rmtree(inplaced, ignore_errors=True)
