# ultraimport

Get control over your imports -- no matter how you run your code.

**Warning: This is an early hack. There are only few unit tests, yet. Maybe not stable!**

[Installation](#installation) | [Quickstart](#quickstart) | [Parameters](#parameters)

[![PyPI Package](https://img.shields.io/pypi/v/ultradict.svg)](https://pypi.org/project/ultraimport)
[![Run Tests](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml)
[![Python >=3.8](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/ronny-rentner/ultraimport.svg)](https://github.com/ronny-rentner/UltraDict/blob/master/license.md)

## Features

- Import any file from the file system as Python code:
    - Works independent of your `sys.path`
    - Works independent of your current working directory
    - Works independent of your top-level package
    - Works no matter if you run your code as a module or as a script
    - Does not care about \_\_init\_\_.py files
    - Can use relative or absolute pathes
- Dynamically wrap your code in a virtual namespace package
- Preprocess code for optimizations (see [example](/examples/working/debug-transform))
- Recursively rewrite subsequent relative import statements (see [example](/examples/working/recurse))
- Dependency injection (see [example](/examples/working/dependency-injection))
- Lazy loading (lazy imports for modules and callables)
- Fix circular imports through lazy imports or dependency injection
- Fix the error: `ImportError: attempted relative import with no known parent package`
- Fix the error: `ValueError: attempted relative import beyond top-level package`
- Better error messages

**General Approach**

ultraimport is built around an own implementation of the [importlib.machinery.SourceFileLoader](https://docs.python.org/3/library/importlib.html#importlib.machinery.SourceFileLoader). This allows to take a different approach on finding code while still being compatible and integrate nicely with the normal Python import machinery. It also allows for some advanced use cases like virtual namespaces, pre-processing, lazy loading, dependency injection and last but not least much better error messages.

**Is ultraimport supposed to replace the normal import statement?**

No! You will continue to use the builtin import statements to import 3rd party libraries which have been installed system wide. `ultraimport` is meant to import local files whose locations you control because they are located relatively to some other files.

**Issues**

Currently, there is no integration with any Python language server for code completion in your IDE.


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

## Quickstart

You can find this quickstart example and others in the [examples/working/](/examples/working) folder.

The [quickstart](/examples/working/quickstart/) folder looks like this:
```
quickstart
├── cherry.py
├── readme.md
├── red
│   ├── cherry.py
│   └── strawberry.py
├── run
│   └── run.py
└── yellow
    ├── banana.py
    └── lemon.py
```

The entry point is the script [run.py](/examples/working/quickstart/run/run.py) located in the [quickstart/run](/examples/working/quickstart/run/) folder.

```python
import ultraimport

# Example 1:
# Import Python module 'cherry.py' from parent folder
cherry = ultraimport('__dir__/../cherry.py')
# <module 'cherry' from '/home/ronny/Projects/py/ultraimport/examples/working/quickstart/cherry.py'>


# Example 2:
# Import another Python module 'cherry.py' from a sibling folder
other_cherry = ultraimport('__dir__/../red/cherry.py')
# <module 'cherry' from '/home/ronny/Projects/py/ultraimport/examples/working/quickstart/red/cherry.py'>


# Example 3:
# Import the `Cherry` object from cherry.py and alias it to the name `my_class`
my_class = ultraimport('__dir__/../red/cherry.py', 'Cherry')
# <class 'cherry.Cherry'>


# Example 4:
# We can make sure my_class is actually the type we expect, a class,
# and my_string is a string, otherwise a TypeError is thrown.
my_class, my_string = ultraimport('__dir__/../cherry.py', { 'MyClass': type, 'some_string': str })
# <class 'cherry.MyClass'>, "I am a string"


# Example 5:
# Or import all objects
objs = ultraimport('__dir__/../cherry.py', '*')
# <class 'cherry.MyClass'>


# Example 6:
# Or them to our local scope
ultraimport('__dir__/../cherry.py', '*', add_to_ns=locals())
# <class 'cherry.MyClass'>



# Example 7:
# The next import would fail because the imported banana.py contains a
# relative import in line 1: `from .. import cherry as relatively_imported_cherry`.
try:
    banana = ultraimport('__dir__/../yellow/banana.py')
except Exception as e:
    pass
    # <class 'ultraimport.ultraimport.ExecuteImportError'>


# Example 8:
# You have two options:
# Put banana.py it in a virtual namespace package using the last 2 folder parts,
# in this case `quickstart.yellow` to make it work.
banana = ultraimport('__dir__/../yellow/banana.py', package=2)
# <module 'quickstart.yellow.banana' from '/home/ronny/Projects/py/ultraimport/examples/working/quickstart/yellow/banana.py'>

# By the way, the other option is more advanced by using recurse=True:
# This will rewrite any relative imports in your code dynamically to use ultraimport().


# Example 9:
# Import cherry.py and put it in a virtual namespace package called `fruit`
# The fruit package is created automatically if it does not exist and the __path__
# is set to the parent folder, in this case `red`.
cherry = ultraimport('__dir__/../red/cherry.py', package='some.fruit')
# <module 'some.fruit.cherry' from '/home/ronny/Projects/py/ultraimport/examples/working/quickstart/red/cherry.py'>


# Example 10:
# After creating the `fruit` namespace package as a side effect of the import,
# we can use it to do classical imports; remember the __path__ of `fruit` points to `red`,
# the parent directory of the cherry.py module we have imported.
from some.fruit.strawberry import Strawberry
# <class 'some.fruit.strawberry.Strawberry'>


# Example 11:
# You could also explicitly create a virtual namespace pointing to the directory 'yellow'
yellow_ns = ultraimport.create_ns_package('yellow', '__dir__/../yellow')
# <module 'yellow' (<_frozen_importlib_external._NamespaceLoader object at 0x7fba8de36920>)>


# Example 12:
# For further imports, you must use the package_name `yellow` as provided as the first argument.
from yellow import lemon
# <module 'yellow.lemon' from '/home/ronny/Projects/py/ultraimport/examples/working/quickstart/yellow/lemon.py'>


# Example 13:
# Let's add some other module from a different directory to our virtual package
ultraimport('__dir__/../red/cherry.py', package='yellow')
from yellow.cherry import Cherry
# <class 'yellow.cherry.Cherry'>
```


## Parameters

`ultraimport(file_path, objects_to_import=None, add_to_ns=None, preprocessor=None, package=None, caller=None, use_cache=True, lazy=False, recurse=False, inject=None, use_preprocessor_cache=True, cache_path_prefix=None)`

`file_path`: path to a file to import, ie. *'my_lib.py'*. It can have any file extension. Please be aware that you must provide the file extension. The path can be relative or absolute. You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`.

`objects_to_import`: provide name of single object or the value `'*'` or an iterable of object names to import from `file_path`. If `lazy=True`, this should be a dict where the values declare the types of the imported objects.

`add_to_ns`: add the `objects_to_import` to the provided namespace. Usually called with `add_to_ns=locals()` if you want the imported module
to be added to the local scope of the caller.

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

## The Issue: Broken Relative Imports in Python

Classically, to do a relative import, your Python script would look like this if you wanted to import
the `logger` object from a `logging.py` module in the same directory:
```python
from .logging import logger

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
    from .logging import logger
ImportError: attempted relative import with no known parent package
```

Python programs or scripts can be executed in a number of different ways and surprisingly, with some of the ways, it even works:
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

You wonder: Why does Python come to a different conclusion depending on the way how I run the program?

The error ***`ImportError: attempted relative import with no known parent package`***
is rather erratic because the code has never changed. sometimes you would also get
***`ValueError: attempted relative import beyond top-level package`***

There actually *is* a known parent package. It's the directory where the code lives in.
Sometimes Python can see it, sometimes not.

Even if there was no parent package, what's the issue with importing a module that
I only know from its relative position to my current module?

With ultraimport your program `run.py` will always find `log.py`, no matter how you run it.
You could change `run.py` to look like this:

run.py:
```python
#!/usr/bin/env python3

# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where run.py is in.
logger = ultraimport('__dir__/logging.py', 'logger')

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



## Python Relative Import Limitations

> Relative imports use a module's __name__ attribute to determine that module's position in the package hierarchy.
> If the module's name does not contain any package information (e.g. it is set to '__main__') then relative imports
> are resolved as if the module were a top level module, regardless of where the module is actually located on the file system.

https://peps.python.org/pep-0328/#relative-imports-and-name

