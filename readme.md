# ultraimport

Get control over your imports -- no matter how you run your code.

**Warning: This is an early hack. There are only few unit tests. Maybe not stable!**

[![PyPI Package](https://img.shields.io/pypi/v/ultradict.svg)](https://pypi.org/project/ultraimport)
[![Run Python Tests](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/ronny-rentner/ultraimport/actions/workflows/ci.yml)

**Features**:
- No more ambiguity: Import any file from the file system as Python code.
- Forget about packages and modules: It's just a file and you can import it.
- Preprocess code for optimizations (see [example](/examples/working/debug-transform))
- Recursively rewrite subsequent relative import statements
- Re-import the same file as often as you want
- Dependency injection (see [example](/examples/working/dependency-injection))
- Lazy loading (lazy imports for modules and callables)
- Fix circular imports through lazy imports or dependency injection
- Fix the error: `ImportError: attempted relative import with no known parent package`
- Fix the error: `ValueError: attempted relative import beyond top-level package`
- Better error messages

**Is ultraimport supposed to replace the normal import statement?**

No, not for now. You will continue to use the builtin import statements to import 3rd party libraries. `ultraimport` is meant to import files whose locations you control because they are located relatively to some other files.

## Installation

Install system wide:
```shell
pip install ultraimport
```

Install a local development version:
```
git clone https://github.com/ronny-rentner/ultraimport.git
pip install -e ./ultraimport
```

## How To Use?

*Note: You can find this and other examples in the [examples](/examples) folder.*

Let's assume your new program in the folder `~/myprogram` looks like this:
```shell
__init__.py
cache.py
log.py
run.py
```

run.py:
```python
#!/usr/bin/env python3

# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where run.py is in.
ultraimport('__dir__/log.py', 'logger', globals=globals())

# Lazy import the cache module. On the first access to any attribute of
# cache, the real cache module will be loaded
cache = ultraimport('__dir__/cache.py', lazy=True)

def main():
    # do something

    logger('I did something')

    cache.store('Something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
```

With `ultraimport`, no matter how you call run.py, it will always find log.py.


## The Python Import Issue

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

Python programs or scripts can be executed in a number of different ways:
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
but in an *ambiguous* way with external dependencies to thinkgs like your current working directory.
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

# Lazy import the cache module. On the first access to any attribute of
# cache, the real cache module will be loaded
cache = ultraimport('__dir__/cache.py', lazy=True)

def main():
    # do something

    logger('I did something')

    cache.store('Something')

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

## Better Error Messages

When an import fails with ultraimport, either a direct `ultraimport()` call or a rewritten relative import using `recurse=True`, ultraimport tries to present a useful error message taht can actually help you solve the problem.

__Example 1:__
Let's try to import the `mypackage.mymodule` module from our [recurse example](/examples/working/recurse), but we'll keep our current working directory (which is this repo checked out).
```pycon
>>> ultraimport('__dir__/examples/working/recurse/mypackage/mymodule')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 738, in __call__
    return ultraimport(*args, caller_level=2, **kwargs)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 638, in ultraimport
    check_file_is_importable(file_path, file_path_orig)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 565, in check_file_is_importable
    raise ResolveImportError('File does not exist.', file_path=file_path_orig, file_path_resolved=file_path)
ultraimport.ResolveImportError: 

┌──────────────────────┐
│ Resolve Import Error │
└──────────────────────┘

An import file could not be found or not be read.

   Import file_path │ __dir__/examples/working/recurse/mypackage/mymodule
 Resolved file_path │ /home/ronny/Projects/py/ultraimport/examples/working/recurse/mypackage/mymodule
    Possible reason │ File does not exist.

 ╲ Did you mean to import '/home/ronny/Projects/py/ultraimport/examples/working/recurse/mypackage/mymodule.py'?
 ╱ You need to add the file extension '.py' to the file_path.

```

You'll get a hint on what was the resolved pathes and when could be the cause of the error. In this case it's a missing file extension because `ultraimport()` imports files.

__Example 2:__
Let's correct the error from our first example and add the .py file extension:
```pycon
>>> ultraimport('__dir__/examples/working/recurse/mypackage/mymodule.py')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 705, in __call__
    return ultraimport(*args, caller_level=2, **kwargs)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 659, in ultraimport
    raise ExecuteImportError('Unhandled, relative import statement found.', file_path=file_path_orig, file_path_resolved=file_path, from_exception=e).with_traceback(e.__traceback__) from None
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 648, in ultraimport
    spec.loader.exec_module(module)
  File "<frozen importlib._bootstrap_external>", line 790, in exec_module
  File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
  File "/home/ronny/Projects/py/ultraimport/examples/working/recurse/mypackage/mymodule.py", line 12, in <module>
    from .logger import log, log as log2
ultraimport.ExecuteImportError: 

┌──────────────────────┐
│ Execute Import Error │
└──────────────────────┘

An import file could be found and read, but an error happened while executing it.

     Source file │ /home/ronny/Projects/py/ultraimport/examples/working/recurse/mypackage/mymodule.py, line 12
      Happend in │ <module>
     Source code │ from .logger import log, log as log2
 Possible reason │ A subsequent, relative import statement was found, but not handled.
 Original errror │ "attempted relative import with no known parent package"

 ╲ To handle the relative import from above, use the ultraimport() parameter `recurse=True`.
 ╱ This will activate automatic rewriting of subsequent, relative imports.

```

Ok, now it found the file `mymodule.py` but in there is another relative import statement for the `logger` module that has failed.

__Example 3:__
We actually have two different options now, but let's follow the suggestion from above and use `recurse=True`.



## Parameters

`ultraimport(file_path, objects_to_import=None, globals=None, preprocessor=None, package=None, caller=None, use_cache=True, lazy=False, recurse=False, inject=None, use_preprocessor_cache=True, cache_path_prefix=None)`

`file_path`: path to a file to import, ie. *'my_lib.py'*. It can have any file extension. Please be aware that you must provide the file extension. The path can be relative or absolute. You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`.

`objects_to_import`: provide name of single object or the value `'*'` or an iterable of object names to import from `file_path`. If `lazy=True`, this should be a dict where the values declare the types of the imported objects.

`globals`: add the `objects_to_import` to the dict provided. Usually called with `gloabls=globals()` if you want the imported module
to be added to the global namespace of the caller.

`preprocessor`: callable that takes the source code as an argument and that can return a modified version of the source code. Check out the [debug-transform example](/examples/working/debug-transform) on how to use the preprocessor.

`package`: can have several modes depending on if you provide a string or an int. If you provide a string, this string will be used as a value of the `__package__` variable of the imported module. If you set an int, it means the number of directories to extract from the `file_path` to calculate the value of `__package__`. Usually you do not have to set this. It can only help in a few cases with nested relative imports when not using the `resurse=True` mode. If `package` is set to `None`, the module will be imported without setting a `__package__`.

`use_cache`: if set to False, allow re-importing of the same source file even if it was imported before.

`lazy`: if set to `True` and if `objects_to_import` is set to `None`, it will lazy import the module. If set to True and `objects_to_import` is a dict, the values of the dict must be the type of the object to lazy import from the module. Currently only the type `callable` is supported.

`recurse`: if set to `True`, a built-in preprocessor is activated to transparently rewrite all `from .. import ..` statements (only relative imports) to ultraimport() calls. Use this mode if you have no control over the source code of the impored modules.

## Contributing

We love contributions!

ultraimport is open source, built on open source, and we'd love to have you hang out in our community.

