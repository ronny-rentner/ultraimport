# ultraimport

Get control over your imports -- no matter how you run your code.

**Warning: This is an early hack. There are only few unit tests, yet. Maybe not stable!**

[Overview](#overview) | [Installation](#installation) | [Quickstart](#quickstart) | [Documentation](#documentation)

[![PyPI Package](https://img.shields.io/pypi/v/ultradict.svg)](https://pypi.org/project/ultraimport)
[![Run Tests](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml)
[![Python >=3.8](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/ronny-rentner/ultraimport.svg)](https://github.com/ronny-rentner/UltraDict/blob/master/license.md)

## Overview

### Features

- Import any file from the file system as Python code:
    - Works independent of your `sys.path`
    - Works independent of your current working directory
    - Works independent of your top-level package
    - Works no matter if you run your code as a module or as a script
    - Does not care about \_\_init\_\_.py files
    - Can use relative or absolute pathes
- Dynamically wrap your code in a virtual namespace package
- Preprocess code for optimizations (see [example](/examples/debug-transform))
- Recursively rewrite subsequent relative import statements (see [example](/examples/recurse))
- Dependency injection (see [example](/examples/dependency-injection))
- Lazy loading (lazy imports for modules and callables)
- Fix circular imports through lazy imports or dependency injection
- Fix the error: `ImportError: attempted relative import with no known parent package`
- Fix the error: `ValueError: attempted relative import beyond top-level package`
- Better error messages

### General Approach

ultraimport is built around an own implementation of the [importlib.machinery.SourceFileLoader](https://docs.python.org/3/library/importlib.html#importlib.machinery.SourceFileLoader). This allows to take a different approach on finding code while still being compatible and integrate nicely with the normal Python import machinery. It also allows for some advanced use cases like virtual namespaces, pre-processing, lazy loading, dependency injection and last but not least much better error messages.

### Is ultraimport supposed to replace the normal import statement?

No! You will continue to use the builtin import statements to import 3rd party libraries which have been installed system wide. `ultraimport` is meant to import local files whose locations you control because they are located relatively to some other files.

### Issues

Currently, there is no integration with any Python language server for code completion in your IDE. Code completion in the Python REPL works as expected.


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

Note: You can find this quickstart example and others in the [examples/](/examples/) folder.

The [quickstart](/examples/quickstart/) folder looks like this:
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

The entry point is the script [run.py](/examples/quickstart/run/run.py) located in the [quickstart/run](/examples/quickstart/run/) folder.
If you want, you can directly execute the example script by running:
```bash
python /path/to/quickstart/run/run.py
```

Inside the `run.py` script, first we import ultraimport:
```python
import ultraimport
```

### 1) Import from parent folder

This example shows how to import the Python module `cherry.py` from the parent folder. Note that `__dir__` in the file path refers to the parent folder of the file that is executing the import. In this case, `run.py` is executing the import and it is located in a folder `run` and thus `__dir__` refers to the `run` folder.

```python
cherry = ultraimport('__dir__/../cherry.py')
# <module 'cherry' from '/home/ronny/Projects/py/ultraimport/examples/quickstart/cherry.py'>
```


### 2) Import from sibling folder

This exmaple show how to import another Python module from a sibling folder.

```python
other_cherry = ultraimport('__dir__/../red/cherry.py')
# <module 'cherry' from '/home/ronny/Projects/py/ultraimport/examples/quickstart/red/cherry.py'>
```


### 3) Import single object

Import the `Cherry` object from `cherry.py` and alias it to the name `my_class`. You could also provide a list of strings
instead of a single string if you want to import multiple objects.

```python
my_class = ultraimport('__dir__/../red/cherry.py', 'Cherry')
# <class 'cherry.Cherry'>
```


### 4) Ensure type of imported object

You can make sure `my_class` is actually the type you expect, a class, and `my_string` is a string, otherwise a `TypeError` is thrown.

```python
my_class, my_string = ultraimport('__dir__/../cherry.py', { 'MyClass': type, 'some_string': str })
# <class 'cherry.MyClass'>, "I am a string"
```


### 5) Import all objects

Using the known special string `'*'` allows to import all objects.

```python
objs = ultraimport('__dir__/../cherry.py', '*')
# <class 'cherry.MyClass'>
```


### 6) Add imported objects to a namespace

You can also provide any dict as a namespace. A common value to use is `globals()`. If you set `add_to_ns=True`,
the imported objects are added to the local scope of the caller.

```python
ultraimport('__dir__/../cherry.py', '*', add_to_ns=globals())
# <class 'cherry.MyClass'>
```


### 7) Give imported module a known parent package

The next import would fail because the imported `banana.py` contains another
relative import in line 1: `from .. import cherry as relatively_imported_cherry`.

```python
try:
    banana = ultraimport('__dir__/../yellow/banana.py')
except Exception as e:
    # <class 'ultraimport.ultraimport.ExecuteImportError'>
    pass
```

If you would try to excute `banana.py` directly, you'd get the famous
`ImportError: attempted relative import with no known parent package` error. To solve
this error, just give the `banana.py` module a known parent package by using the `package` parameter.
The relative import from above has two dots, so it means go two levels up. Thus we need to
give our `banana.py` module at least two levels of parent packages by using `package=2`.

```python
banana = ultraimport('__dir__/../yellow/banana.py', package=2)
# <module 'quickstart.yellow.banana' from '/home/ronny/Projects/py/ultraimport/examples/quickstart/yellow/banana.py'>
```


### 8) Embed module in a virtual namespace package

You can also provide a string for the `package` parameter to define the name of the package. In this case
we create a package called `fruit` pointing at the parent directory of `cherry.py`, the file that is being
imported.

```python
cherry = ultraimport('__dir__/../red/cherry.py', package='some.fruit')
# <module 'some.fruit.cherry' from '/home/ronny/Projects/py/ultraimport/examples/quickstart/red/cherry.py'>
```


### 9) Integrate with normal imports

After creating the `fruit` namespace package as a side effect of the import, you can use it to do classical imports.
Remember that the `fruit` package points to the directory `red`.

```python
from some.fruit.strawberry import Strawberry
# <class 'some.fruit.strawberry.Strawberry'>
```


### 10) Create virtual namespace package

You could also explicitly create a virtual namespace pointing to the directory `'yellow'`. Note that `__dir__` in the path below refers to the parent folder of the file that is executing the import.

```python
yellow_ns = ultraimport.create_ns_package('yellow', '__dir__/../yellow')
# <module 'yellow' (<_frozen_importlib_external._NamespaceLoader object at 0x7fba8de36920>)>
```

For further imports, the package_name `yellow` must be used as provided as the first argument.

```python
from yellow import lemon
# <module 'yellow.lemon' from '/home/ronny/Projects/py/ultraimport/examples/quickstart/yellow/lemon.py'>
```

Let's add some other module `cherry.py` from a different directory to our virtual package. After
you have added the module to the package, you can again use normal Python imports
to access it.

```python
ultraimport('__dir__/../red/cherry.py', package='yellow')
from yellow.cherry import Cherry
# <class 'yellow.cherry.Cherry'>
```


## Documentation

The [full interface documentation](/docs/) can be find in the [docs/](/docs/) folder. This is just an excerpt of the main function.

## `ultraimport` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L58)</kbd>

```python
ultraimport(
    file_path,
    objects_to_import=None,
    add_to_ns=None,
    preprocessor=None,
    package=None,
    caller=None,
    use_cache=True,
    lazy=False,
    recurse=False,
    inject=None,
    use_preprocessor_cache=True,
    cache_path_prefix=None
)
```

Import Python code files from the file system. This is the central main function of ultraimport.

**Parameters:**

 - **`file_path`** _(str)_:  Path to the module file that should be imported. It can have any file extension. Please be aware that you must provide the file extension. The path can be relative or absolute. You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`.

 - **`objects_to_import`** _(str | (Iterable[str] | Dict[str, object])_:  Can have several modes depending on the type of the parameter.
    - (str): Name of a single object to import from the module in `file_path`. The special value `'*'` selects all objects from that module.
    - (Iterable[str]): A list of names of objects to import.
    - (Dict[str, object]): The keys represent the names of the objects to import. The values define the expected types of those objects. A `TypeError` is thrown if the types don't match the expectation. If you set `lazy=True`, you must use a dict for `objects_to_import` and define the types.

 - **`add_to_ns`** _(Dict[str, object])_:  add the `objects_to_import` to the dict provided. Usually called with `add_to_ns=locals()` if you want the imported module to be added to the global namespace of the caller.

 - **`preprocessor`** _(callable)_:  Takes the source code as an argument and can return a modified version of the source code. Check out the [debug-transform example](/examples/debug-transform) on how to use the preprocessor.

 - **`package`** _(str | int)_:  Can have several modes depending on if you provide a string or an integer. If you provide a string, ultraimport will generate one or more namespace packages and use it as parent package of your imported module. If you set an integer, it means the number of path parts (directories) to extract from the `file_path` to calculate the namespace package. This can help with subsequent relative imports in your imported files. If `package` is set to the default `None`, the module will be imported without setting it parent `__package__`.

 - **`use_cache`** _(bool)_:  If set to `False`, allows re-importing of the same source file even if it was imported before. Otherwise a cached version of the imported module is returned.

 - **`lazy`** _(bool)_:  *Experimental* *wip* If set to `True` and if `objects_to_import` is set to `None`, it will lazy import the module. If set to True and `objects_to_import` is a dict, the values of the dict must be the type of the object to lazy import from the module. Currently only the type `callable` is supported.

 - **`recurse`** _(bool)_:  If set to `True`, a built-in preprocessor is activated to transparently rewrite all relative import statements (those with a dot like `from . import something`) to ultraimport() calls. Use this mode if you have no control over the source code of the impored modules.

 - **`cache_path_prefix`** _(str)_:  Directory for storing preprocessed files. If you use the preprocessor feature or if you use the option `recurse=True` (which in turn uses the preprocessor feature) you will have the option to store the resulting code after preprocessing. By default, they are stored in parallel to the original source code files, but this option allows to override to location. One common setting is `cache_path_prefix='__pycache__'` to store the processed files along with the bytecode files.
 - **`_Note_`**:  Even when you change this directory, this will be hidden from Python. Towards Python, the preprocessed files will always look like they are in the same directory as the original source code files, even if they are not.

**Returns:**
 Depending on the parameters *returns one of the following*:

 - **`object`**:  If `objects_to_import` is `None`, returns a single module object.

 - **`object`**:  If `objects_to_import` is a `str`, returns the single object with the specified name from the imported module.

 - **`dict`**:  If `objects_to_import` has the value `'*'`, returns a dict of all items from the imported module.

 - **`list`**:  If `objects_to_import` is a `List[str]`, return a list of imported objects from the imported module.

### Advanced Usage

See [docs/advanced-usage.md](/docs/advanced-usage.md)


### Better Error Messages

See [docs/better-error-messages.md](/docs/better-error-messages.md)


### Contributing

We love contributions!

ultraimport is open source, built on open source, and we'd love to have you hang out in our community.


## The Issue: Relative Imports in Python

Classically, to do a relative import, your Python script `run.py` would look like this if you wanted to import
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

The error **`ImportError: attempted relative import with no known parent package`**
is rather erratic because the code has never changed. Sometimes you would also get
**`ValueError: attempted relative import beyond top-level package`**.

There actually *is* a known parent package. It's the directory where the code lives in.
Sometimes Python can see it, sometimes not.

Even if there was no parent package, what's the issue with importing a module that
I only know from its relative position to my current module?

With ultraimport your program `run.py` will always find `logging.py` in the same directory,
no matter how you run it. You could change it to look like this:

```python
#!/usr/bin/env python3

# ultraimport needs to be installed and imported in the classical way
import ultraimport

# Import the 'logger' object from 'logging.py' that is located in the same
# directory as this file.
# Note: `__dir__` refers to the directory where this file is in.
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

### Python Relative Import Limitations

> https://peps.python.org/pep-0328/#relative-imports-and-name
>
> Relative imports use a module's __name__ attribute to determine that module's position in the package hierarchy.
> If the module's name does not contain any package information (e.g. it is set to '__main__') then relative imports
> are resolved as if the module were a top level module, regardless of where the module is actually located on the file system.

