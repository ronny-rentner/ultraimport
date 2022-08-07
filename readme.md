# ultraimport

Get control over your imports -- no matter how you run your code.

**Warning: This is an early hack. There are only few unit tests, yet. Maybe not stable!**

[![PyPI Package](https://img.shields.io/pypi/v/ultradict.svg)](https://pypi.org/project/ultraimport)
[![Run Tests](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml)
[![Python >=3.8](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/ronny-rentner/ultraimport.svg)](https://github.com/ronny-rentner/UltraDict/blob/master/license.md)

**Features**:
- Import any file from the file system as Python code
- Works independent of your `sys.path`, independent of your current working directory, and independent of your top-level package
- Works no matter if you run your code as a module or as a script
- Dynamically wrap your code in a virtual namespace package
- Preprocess code for optimizations (see [example](/examples/working/debug-transform))
- Recursively rewrite subsequent relative import statements (see [example](/examples/working/recurse))
- Dependency injection (see [example](/examples/working/dependency-injection))
- Lazy loading (lazy imports for modules and callables)
- Fix circular imports through lazy imports or dependency injection
- Fix the error: `ImportError: attempted relative import with no known parent package`
- Fix the error: `ValueError: attempted relative import beyond top-level package`
- Better error messages

**Is ultraimport supposed to replace the normal import statement?**

No! You will continue to use the builtin import statements to import 3rd party libraries which have been installed system wide. `ultraimport` is meant to import local files whose locations you control because they are located relatively to some other files.

**How does it work?**

## Installation

Install system wide:
```shell
pip install ultraimport
```

Install a local development version:
```shell
git clone https://github.com/ronny-rentner/ultraimport.git
pip install -e ./ultraimport
```

## How To Use?

*Note: You can find [this](/examples/working/myprogram) and other examples in the [examples/working/](/examples/working) folder.*

Let's assume your new program in the folder `~/myprogram` looks like this:
```shell
cache.py
log.py
run.py
```

You have split the code into 3 modules, but it is not worth it to use a more complex directory structure.

run.py:
```python
#!/usr/bin/env python3

# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where run.py is in.
ultraimport('__dir__/log.py', 'logger', globals=globals())

def main():
    # do something
    logger('I did something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
```

With `ultraimport`, no matter how you call run.py, it will always find log.py.


## The Issue: Relative Import in Python

Classically, to do a relative import, your run.py would look like this:
```python
#!/usr/bin/env python3

from .log import logger

def main():
    # do something

    logger('I did something')

if __name__ == 'main':
    main()
```

If you try to run the program in usual way, you'll get an error message:

```shell
$ python ./run.py
Traceback (most recent call last):
  File "/home/user/myprogram/./run.py", line 1, in <module>
    from .log import logger
ImportError: attempted relative import with no known parent package
```

Python programs or scripts can be executed in a number of different ways and with some of the ways, it even works:
```shell
# Broken
python ~/myprogram/run.py

# Works
cd ~
python -c 'import myprogram.run'

# Works
python -m myprogram.run

# Broken
cd ~/myprogram
python -c 'import run'

# Broken
python -m run

# Broken
python ./run.py

# Broken
~/myprogram/run.py
```

The error ***ImportError: attempted relative import with no known parent package***
is rather erratic because the code has never changed.

There actually *is* a known parent package. It's the directory where the code lives in.
Sometimes Python can see it, sometimes not.

Even if there was no parent package, what's the issue with importing a module that
I only know from its relative position to my current module?

The main problem with the orignal Python imports is that they are ambiguous. As a programmer,
you work on source code files in the file system. But Python doesn't import source code files
from the file system. It imports packages and modules. The structure of the directories and files
in your file system is somehow mapped to the structure of packages and modules in Python,
but in an *ambiguous* way with additional, external dependencies to things like your current working directory.
This is bad, because you need to write more code to handle these external dependencies that you never wanted.
All the information you have about your source code files is information about their relative
location to each other in the file system.

## The Solution: ultraimport

With ultraimport your program `run.py` will always find `log.py`, no matter how you run it.

run.py:
```python
#!/usr/bin/env python3

# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where run.py is in.
ultraimport('__dir__/log.py', 'logger', globals=globals())

def main():
    # do something
    logger('I did something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
```

As you can see, you'll have to import ultraimport in the classical way. It's intended to be installed as a system-wide library.
Afterwards, you can import your own code based on relative or absolute file system paths so it can always be found.

With ultraimport, Python code can be executed in an way and the imports keep working:
```shell
# Works
python ~/myprogram/run.py

# Works
cd ~
python -c 'import myprogram.run'

# Works
python -m myprogram.run

# Works
cd ~/myprogram
python -c 'import run'

# Works
python -m run

# Works
python ./run.py

# Works
~/myprogram/run.py
```

## Parameters

`ultraimport(file_path, objects_to_import=None, globals=None, preprocessor=None, package=None, caller=None, use_cache=True, lazy=False, recurse=False, inject=None, use_preprocessor_cache=True, cache_path_prefix=None)`

`file_path`: path to a file to import, ie. *'my_lib.py'*. It can have any file extension. Please be aware that you must provide the file extension. The path can be relative or absolute. You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`.

`objects_to_import`: provide name of single object or the value `'*'` or an iterable of object names to import from `file_path`. If `lazy=True`, this should be a dict where the values declare the types of the imported objects.

`globals`: add the `objects_to_import` to the dict provided. Usually called with `gloabls=globals()` if you want the imported module
to be added to the global namespace of the caller.

`preprocessor`: callable that takes the source code as an argument and that can return a modified version of the source code. Check out the [debug-transform example](/examples/working/debug-transform) on how to use the preprocessor.

`package`: can have several modes depending on if you provide a `string` or an `int`. If you provide a string, ultraimport will generate one or more namespace packages and use it as parent package of your imported module. If you set an int, it means the number of path parts (directories) to extract from the `file_path` to calculate the namespace package. Usually you do not have to set this. It can only help in a few cases with nested relative imports when not using the `resurse=True` mode. If `package` is set to `None`, the module will be imported without setting it parent `__package__`.

`use_cache`: if set to False, allow re-importing of the same source file even if it was imported before. Otherwise a cached version of the imported module is returned.

`lazy`: if set to `True` and if `objects_to_import` is set to `None`, it will lazy import the module. If set to True and `objects_to_import` is a dict, the values of the dict must be the type of the object to lazy import from the module. Currently only the type `callable` is supported.

`recurse`: if set to `True`, a built-in preprocessor is activated to transparently rewrite all `from .. import ..` statements (only relative imports) to ultraimport() calls. Use this mode if you have no control over the source code of the impored modules.

`cache_path_prefix`: Directory for storing preprocessed files. If you use the preprocessor feature or if you use the option `recurse=True` (which in turn uses the preprocessor feature) you will have the option to store the resulting code after preprocessing. By default, they are stored in parallel to the original source code files, but this option allows to override to location. One common setting is `cache_path_prefix='__pycache__'` to store the processed files along with the bytecode files. __Note:__ Even when you change this directory, this will be hidden from Python. Towards Python, the preprocessed files will always look like they are in the same directory as the original source code files, even if they are not.

## Advanced Usage

See [docs/advanced-usage.md](/docs/advanced-usage.md)

## Better Error Messages

See [docs/better-error-messages.md](/docs/better-error-messages.md)

## Contributing

We love contributions!

ultraimport is open source, built on open source, and we'd love to have you hang out in our community.

