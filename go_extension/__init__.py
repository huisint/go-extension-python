# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
__version__ = "0.0.0"

import setuptools.command.build_ext

from .extension import GoExtension
from .compiler import GoPyCompiler
from .build_ext import build_ext as _build_ext
from . import exceptions

__all__ = [
    "GoExtension",
    "GoPyCompiler",
    "exceptions",
]

setattr(setuptools.command.build_ext, "build_ext", _build_ext)
