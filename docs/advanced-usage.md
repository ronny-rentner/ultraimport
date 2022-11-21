# ultraimport: Advanced Usage

Check the [ultraimport Github Page](https://github.com/ronny-rentner/ultraimport) for an overview and basic usage information.

### 1. Import impossible filenames and directory names

With ultraimport, you can import from any file or directory, even if it contains spaces or dashes or if the file name contains any other file extension.

See [working/impossible-filename](/working/impossible-filename)

run.py:
```python
import ultraimport

ultraimport('__dir__/im possible-dir ectory/my lib.python3')
```

### 2. Typed imports

Get type safety by specifying what type you expect a certain imported object to be.

See [working/typed-imports](/working/typed-imports)

run.py:
```python
import ultraimport, typing

myfunction, mystring = ultraimport('__dir__/mylib.py', { 'myfunction': typing.Callable, 'mystring': str })

print(myfunction, type(myfunction))
print(mystring, type(mystring))

try:
    myint = ultraimport('__dir__/mylib.py', { 'myint': str })

    # If we reach this point, the exception wasn't thrown
    print('No type mismatch detected')

    print(myint, type(myint))

except TypeError as e:
    print('Type mismatch detected')
    print(e)
```

### 3. Preprocessing

See [working/debug-transform](/working/debug-transform)


### 4. Dynamic Namespace

When importing Python code files from the filesystem, one issue is if they contain further relative imports. Those relative imports
depend on a package or namespace package. Thus, ultraimport can dynamically put your module in a namespace so those subsequent relative imports continue to work.

See [working/dynamic-namespace](/working/dynamic-namespace)

Our main.py looks like this:
```python
from .lib import lib

print(lib)

import sys
print(sys.modules[lib.__package__])
```

If you run this code from the root of the git repository, you'll get:
```shell
$ python working/dynamic-namespace/main.py
Traceback (most recent call last):
  File "/home/ronny/Projects/py/ultraimport/working/dynamic-namespace/main.py", line 1, in <module>
    from . import lib
ImportError: attempted relative import with no known parent package
```

If we use ultraimport, we can dynamically wrap a namespace package around main.py so Python thinks it has a parent package:
```pycon
>>> import ultraimport
>>> main = ultraimport('working/dynamic-namespace/main.py', package='mypackage')
Hello world from lib.py
utils: <module 'mypackage.utils' from '/home/ronny/Projects/py/ultraimport/working/dynamic-namespace/utils.py'>
<module 'mypackage.lib.lib' from '/home/ronny/Projects/py/ultraimport/working/dynamic-namespace/lib/lib.py'>
<module 'mypackage.lib' (namespace)>
```

We could also automatically derrive the package name from the parent directories by using an int as a value to `package`:
```pycon
>>> import ultraimport
>>> main = ultraimport('working/dynamic-namespace/main.py', package=2)
Hello world from lib.py
utils: <module 'working.dynamic-namespace.utils' from '/home/ronny/Projects/py/ultraimport/working/dynamic-namespace/utils.py'>
<module 'working.dynamic-namespace.lib.lib' from '/home/ronny/Projects/py/ultraimport/working/dynamic-namespace/lib/lib.py'>
<module 'working.dynamic-namespace.lib' (namespace)>
```

### 3. Dependency Injection

See [working/dependency-injection](/working/dependency-injection)


