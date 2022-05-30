ultraimport -  Stable Python Imports
------------------------------------

Python import system is not based on files. It's based on packages and modules, on directories and a lot of magic.

`ultraimport` gives you stable imports no matter how you run your code. `ultraimport` will always find and import the same code files.

** Warning: This is an early hack. No unit tests exist. Maybe not stable! **

The Issue (with Classic Python Imports)
---------------------------------------

Let's assume you have created a small Python program called `run.py`. It lives together with a small
module `log.py` in the same directory call `myprogram`. Sometimes, you also import run.py in other
programs because it has some useful functions.

The directory looks like this:
```shell
$ ls
__init__.py  log.py  __pycache__  run.py
```

Python code can be executed in a number of different ways.

```shell
python /home/user/myprogram/run.py
cd /home/user/
python -c 'import myprogram.run'
python ./mypackage/mymodule.py
python -m mypackage.mymodule
cd mypackage
python -c 'import mymodule'
python -m mymodule
python ./mymodule.py
```

The program looks like this:

```python
from .log import logger

def main():
    # do something

    logger('I did something')

if __name__ == 'main':
    main()
```

This is just a demo. The program does not do anything apart from printing a log message through a log module helper that lives next
to the program in the same directly. As `log` is a very common name, it's better to do an explicit, relative import to make sure
we're actually importing the right log module that belongs to use and not some other log module from somewhere in the `sys.path`

If you try to run the program, you'll get an error message:

```shell
$ python ./run.py
Traceback (most recent call last):
  File "/home/user/myprogram/./run.py", line 1, in <module>
    from .log import logger
ImportError: attempted relative import with no known parent package
```

The error **ImportError: attempted relative import with no known parent package** is rather erratic and wrong. There is
a known parent package. It's the directory where the code lives in. Without any code changes you can do

```
$ cd ..
$ python -m myprogram.run
I did something
```

The Solution: ultraimport
-------------------------

So how can we make our code always work independent of how you run it?

We could rewrite the code to do a so called absolute import (they're not really absolute) but that would create a risk of not
importing the right log module, depending on the directory list of `sys.path`.

Though, we do have a safe information we can rely on: The `log.py` module lives next to us in the same directory.
There was just no way to tell Python to load it from there. 

`ultraimport` can do this.

With ultraimport your program will look like this:

```python
#!/usr/bin/env python3

import ultraimport

ultraimport('log.py', 'logger')

def main():
    # do something

    logger('I did something')

if __name__ == 'main':
    main()
```

As you can see, you'll have to import ultraimport in the classical way. It's intended to be installed as a system-wide library.
Afterwards, you can import your own code based on relative or absolute file system paths so it can always be found.


**Features**:

- import any file as Python code, no matter what the extension is
- imports always import the same files no matter how


License
-------

This project is Copyright (c) Ronny Rentner and licensed under
the terms of the GNU GPL v3+ license.

Contributing
------------

We love contributions! ultraimport is open source,
built on open source, and we'd love to have you hang out in our community.
