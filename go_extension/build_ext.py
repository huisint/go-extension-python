# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
from setuptools.command import build_ext as _build_ext
from setuptools.extension import Extension
from setuptools import dist, dep_util
from setuptools._distutils import log
from pathlib import Path

from go_extension import extension, compiler


class build_ext(_build_ext.build_ext):  # type: ignore
    """Command `build_ext` able to build GoExtension.

    If you change `go` command, inherit this class and pass it to setuptools.setup() like this.

    >>> from setuptools import setup
    >>> from go_extension import build_ext
    >>> class build_ext(build_ext.build_ext):
    ...     go_command = 'path/to/go(executable)'
    >>> setup(cmdclass={'build_ext': build_ext})  # doctest: +SKIP
    """

    go_command: str = "go"
    gopycompiler: compiler.GoPyCompiler

    def __init__(self, distr: dist.Distribution) -> None:
        super().__init__(distr)
        self.gopy_compiler = compiler.GoPyCompiler()

    def run(self) -> None:
        self.gopy_compiler = compiler.GoPyCompiler(
            go_command=self.go_command,
            verbose=bool(getattr(self, "verbose", False)),
            dry_run=bool(getattr(self, "dry_run", False)),
            force=bool(getattr(self, "force", False)),
            inplace=bool(getattr(self, "inplace", False)),
        )
        super().run()

    def build_extension(self, ext: Extension) -> None:
        if isinstance(ext, extension.GoExtension):
            self.build_go(ext)
        else:
            super().build_extension(ext)

    def build_go(self, ext: extension.GoExtension) -> None:
        """Build GoExtension.

        Parameters
        ----------
        ext : go_extension.extension.GoExtension
            A GoExtension object to build.
        """
        assert isinstance(ext, extension.GoExtension)
        if self.should_skip_ext(ext):
            log.debug("skipping '%s' extension (up-to-date)", ext.original_name)
            return
        else:
            log.info("building '%s' extension", ext.original_name)
        if self.gopy_compiler.inplace:
            # Reference: setuptools.command.build_ext.build_ext.copy_extensions_to_source()
            build_py = self.get_finalized_command("build_py")
            fullname = str(self.get_ext_fullname(ext.name))
            modpath = fullname.split(".")
            package = ".".join(modpath[:-1])
            package_dir = build_py.get_package_dir(package)
            # end
            self.gopy_compiler.generate(ext, output=Path(package_dir))
        ext_path = self.get_ext_fullpath(ext.name)
        self.gopy_compiler.build(ext, output=Path(ext_path).parent)

    def should_skip_ext(self, ext: Extension) -> bool:
        """Return true if the extension should be skipped.

        Parameters
        ----------
        ext : setuptools.extension.Extension

        Returns
        -------
        bool
        """
        ext_path = self.get_ext_fullpath(ext.name)
        depends = ext.sources + ext.depends
        return not (self.force or dep_util.newer_group(depends, ext_path, "newer"))
