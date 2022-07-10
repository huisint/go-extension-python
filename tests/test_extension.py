# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
from unittest import TestCase
import doctest

from go_extension import extension


class TestGoExtension___init__(TestCase):
    name: str = "mypkg.go"
    packages: list[str] = ["github.com/hoge/fuga/tests/go"]

    def setUp(self) -> None:
        self.ext = extension.GoExtension(
            name=self.name,
            packages=self.packages,
        )

    def test_name(self) -> None:
        self.assertEqual(
            self.name + "._" + self.ext._compiled_name,
            self.ext.name,
        )


class TestGoExtension_property(TestCase):
    name: str = "mypkg.go"
    packages: list[str] = ["github.com/hoge/fuga/tests/go"]

    def setUp(self) -> None:
        self.ext = extension.GoExtension(
            name=self.name,
            packages=self.packages,
        )

    def test_packages(self) -> None:
        self.assertSequenceEqual(self.ext.packages, self.packages, seq_type=list)

    def test_original_name(self) -> None:
        self.assertEqual(self.ext.original_name, self.name)


def load_tests(loader, tests, _):  # type: ignore
    tests.addTests(doctest.DocTestSuite(extension))
    return tests
