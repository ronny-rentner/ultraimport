ultraimport -  Stable, File-based Python Imports
------------------------------------------------

`ultraimport` gives you stable, reliable, repeatable imports -- no matter how you run your code.

**Features**:

- import any file from the file system as Python code
- reliable relative imports
- re-import the same as often as you want

**Warning: This is an early hack. No unit tests exist. Maybe not stable!**

Installation
------------

```shell
pip install ultraimport
```

```
git clone https://github.com/ronny-rentner/ultraimport.git
pip install -e ./ultraimport
```

How To Use?
-----------

Let's assume your program folder looks like this:
```shell
$ ls myprogram/
__init__.py
cache.py
log.py
run.py
```

run.py:
```python
#!/usr/bin/env python3

import ultraimport

# `__dir__` refers to the directory where log.py is in
ultraimport('__dir__/log.py', 'logger', globals=globals())

# Alias objects after import
store, load = ultraimport('__dir__/cache.py', ('store', 'load'))

def main():
    # do something

    logger('I did something')

if __name__ == '__main__':
    main()
```

Now, no matter how you call run.py, it will always find log.py.


The Issue With Python Imports
-----------------------------

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

If you try to run the program in the *wrong* way, you'll get an error message:

```shell
$ python ./run.py
Traceback (most recent call last):
  File "/home/user/myprogram/./run.py", line 1, in <module>
    from .log import logger
ImportError: attempted relative import with no known parent package
```

Python code can be executed in a number of different ways:
```shell
# Broken
python ~/myprogram/run.py

# Works
cd ~
python -c 'import myprogram.run'

# Works
python -m myprogram.run

# Broken
cd myprogram
python -c 'import run'

# Broken
python -m run

# Broken
python ./run.py

# Broken
/home/ronny/Projects/myprogram/run.py
```

The error ***ImportError: attempted relative import with no known parent package***
is rather erratic because the code has never changed.

There actually is a known parent package. It's the directory where the code lives in.
Sometimes Python can see it, sometimes not.

The Solution: ultraimport
-------------------------

With ultraimport your program will always find log.py, no matter how you run it.

```python
#!/usr/bin/env python3

import ultraimport

ultraimport('__dir__/log.py', 'logger', globals=globals())

def main():
    # do something

    logger('I did something')

if __name__ == '__main__':
    main()

```

As you can see, you'll have to import ultraimport in the classical way. It's intended to be installed as a system-wide library.
Afterwards, you can import your own code based on relative or absolute file system paths so it can always be found.

## Parameters

`def ultraimport(file_path, objects_to_import = None, globals=None, caller=None, use_cache=True)`

`file_path`: path to a file to import, ie. *'my_lib.py'*. It can have any file extension. Please be aware that you must provide the file extension.
The path can be relative or absolute. You can use the special string `__dir__` to refer to the director of the caller which will be derived
via inspetions. If you use advanced debugging tools you might have to set `caller=__file__`.

`objects_to_import`: provide name of single object or the value `'*'` or an iterable of object names to import from file_path.

`globals`: add the `objects_to_import` to the dict provided. Usually called with `gloabls=globals()` if you want the imported module
to be added to the globals of the caller.

`use_cache`: if set to false, allow re-importing of the same source file even if it was cached before.


Contributing
------------

We love contributions! ultraimport is open source,
built on open source, and we'd love to have you hang out in our community.
