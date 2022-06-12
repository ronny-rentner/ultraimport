# ultraimport -  File-based Python Imports

`ultraimport` gives you reliable, local imports -- no matter how you run your code.

**Features**:

- import any file from the file system as Python code
- forget about packages and modules, it's just a file and you can import it!
- preprocess code for optimizations
- re-import the same file as often as you want
- lazy loading (lazy imports for modules and callables)
- fix circular imports through lazy imports
- fix the error: `ImportError: attempted relative import with no known parent package`
- fix the error: `ValueError: attempted relative import beyond top-level package`

**Warning: This is an early hack. No unit tests exist. Maybe not stable!**

Is `ultraimport` supposed to replace the normal import statement?

No, not for now. The normal import statement will continue to exist to import 3rd party libraries. `ultraimport` is meant to import files whose locations you control because they are located relatively to some other files.

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

# `__dir__` refers to the directory where run.py is in
ultraimport('__dir__/log.py', 'logger', globals=globals())

# alias objects after import
store, load = ultraimport('__dir__/cache.py', ('store', 'load'))

def main():
    # do something

    logger('I did something')

if __name__ == '__main__':
    main()
else:
    logger('I have been imported')
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

## The Solution: ultraimport

With ultraimport your program `run.py` will always find `log.py`, no matter how you run it.

run.py:
```python
#!/usr/bin/env python3

import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
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

Python code can be executed in a number of different ways:
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

`def ultraimport(file_path, objects_to_import = None, globals=None, preprocessor=None, caller=None, use_cache=True, lazy=False)`

`file_path`: path to a file to import, ie. *'my_lib.py'*. It can have any file extension. Please be aware that you must provide the file extension. The path can be relative or absolute. You can use the special string `__dir__` to refer to the directory of the caller which will be derived
via inspetions. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`.

`objects_to_import`: provide name of single object or the value `'*'` or an iterable of object names to import from file_path. If `lazy=True`, this should be a dict where the values declare the types of the imported objects.

`globals`: add the `objects_to_import` to the dict provided. Usually called with `gloabls=globals()` if you want the imported module
to be added to the globals of the caller.

`preprocessor`: callable that takes the source code as an argument and that can return a modified version of the source code.

`use_cache`: if set to False, allow re-importing of the same source file even if it was import before.

`lazy`: if set to True and if objects_to_import is set to None, it will lazy import the module. If set to True and objects_to_import is a dict, the values of the dict must be the type of the object to lazy import from the module. Currently only the type 'callable' is supported.


## Contributing

We love contributions!

ultraimport is open source, built on open source, and we'd love to have you hang out in our community.

