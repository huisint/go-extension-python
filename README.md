# go-extension

go-extension provides `GoExtension` class that is given as one of `ext_modules` argument to `setuptools.setup()` to generate and compile a CPython extension module from Go pacakges.


## Requirements

- Python3.10 or later
- Go1.16 or later (in order to build)


## Installation
```shell
$ pip install go-extension
```

## Getting Started
```python
from setuptools import setup
from go_extension import GoExtension

ext = GoExtension(
    name='hello_go',
    packages=['github.com/huisint/go-extension-python/hello']
)

import sys
sys.argv = ['', 'build_ext', '--inplace'] # To call `build_ext` command of setup().
setup(ext_modules=[ext])

from hello_go import hello
print()
hello.hello_world() # print "Hello, World"
hello.greet('Go')   # print "Hello, Go"
```

### Go package in Python project root
Now you have `py_pkg` and `go_pkg` in project root.
The following shows how to build `go_pkg` as a Python package named `py_pkg/go`.

```
project-root
│
├─go_pkg
│   └─main.go # package hello
│
└─py_pkg
    └─__init__.py
```


First, init your project root as Go module by running:
```shell
$ go mod init example.com/foo/bar
```


Second, create `setup.py` like this:

```python
from setuptools import setup
from pathlib import Path
try:
    from go_extension import GoExtension
except (ImportError, ModuleNotFoundError):
    from pip._internal.cli import main as pip
    pip.main(['install','-U','go-extension'])
    from go_extension import GoExtension

ext = GoExtension(
    name='py_pkg.go',
    pakcages=['example.com/foo/bar/go_pkg'],
    sources=[file.as_posix() for file in Path('go_pkg').glob('*.go') if file.is_file()]
)

setup(
    ext_modules=[ext]
)
```


Third, build the extension by running:
```shell
$ python setup.py build_ext --inplace
```


Now you can import the Go package as a Python module like:
```python
from py_pkg.go import hello
hello.do_something()
```

```
project-root 
│
├─go_pkg
│   └─main.go
│
├─py_pkg
│   ├─go
│   │  ...
│   └─__init__.py
│   
├─go.mod
└─setup.py
```


### Distributions
`Go` is **NOT** required to run the compiled Python bindings.


You can build a wheel as a distribution by running:
```shell
$ pip install -U wheel
$ python setup.py bdist_wheel
```


### Options

If your go command is not `go`, then inherit `go_extension.build_ext.build_ext_go` and change `go_command` property.
```python
from setuptools import setup
from go_extension.build_ext import build_ext_go

class build_ext(build_ext_go):
    go_command = 'path/to/go'

setup(
    cmdclass={'build_ext': build_ext}
)
```

## License
MIT License
