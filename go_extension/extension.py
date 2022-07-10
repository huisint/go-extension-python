# Copyright (c) 2021 Shuhei Nitta. All rights reserved.
from setuptools import extension
import typing as t


class GoExtension(extension.Extension):  # type: ignore
    """Extension written in Go language.

    Examples
    --------
    >>> from setuptools import setup
    >>> from go_extension import GoExtension

    >>> ext = GoExtension(
    ...     name='hello_go',
    ...     packages=['github.com/huisint/go-extension-python/hello']
    ... )

    >>> setup(ext_modules=[ext])  # doctest: +SKIP
    """

    _original_name: str
    _packages: list[str]
    _compiled_name: str = "go"
    name: str
    sources: list[str]
    depends: list[str]

    def __init__(
        self,
        name: str,
        packages: t.Sequence[str],
        sources: t.Optional[list[str]] = None,
        *args: t.Any,
        **kwargs: t.Any,
    ) -> None:
        """
        Parameters
        ----------
        name : str
            The package name. Similar to that of setuptools.extension.Exention.
        packages : Sequence[str]
            A sequence of Go packages.
            If your project root is also go package root named `github.com/foo/bar`
            (which means 'go.mod' file exists in your progect root),
            and you have go pacakge named 'go_pkg' in your project root,
            set `packages=['github.com/foo/bar/go_pkg']`.
        sources : list[str] | None
            Source files of GoExtension (optional).
            This is used just to judge whether sources have been updated.
        *args, **kwargs : Any
            The same parameters as setuptools.extension.Extension.
        """
        super().__init__(
            f"{name}._{self._compiled_name}",
            sources or [],
            *args,
            **kwargs,  # the same name as .so file gopy creates
        )
        self._original_name = str(name)
        self._packages = [str(pkg) for pkg in packages]

    @property
    def packages(self) -> list[str]:
        """List of Go package."""
        return self._packages

    @property
    def original_name(self) -> str:
        return self._original_name
