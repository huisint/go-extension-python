# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
__version__ = "0.0.1"

import setuptools.command.build_ext

from .extension import GoExtension  # noqa
from .compiler import GoPyCompiler  # noqa
from .build_ext import build_ext as _build_ext
from . import exceptions  # noqa

setattr(setuptools.command.build_ext, "build_ext", _build_ext)
