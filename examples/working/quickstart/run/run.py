#!/usr/bin/env python3

import ultraimport

# Import Python module 'cherry.py' from parent folder
cherry = ultraimport('__dir__/../cherry.py')
print(cherry, '\n', dir(cherry), '\n')

# Import another Python module 'cherry.py' from a sibling folder
other_cherry = ultraimport('__dir__/../red/cherry.py')
print(other_cherry, '\n', dir(other_cherry), '\n')

# Import MyClass object from cherry.py and alias it to the name `my_class`
my_class = ultraimport('__dir__/../cherry.py', 'MyClass')
print(my_class, '\n', dir(my_class), '\n')

# We can make sure my_class is actually the type we expect, a class,
# and my_string is a string, otherwise a TypeError is thrown.
my_class, my_string = ultraimport('__dir__/../cherry.py', { 'MyClass': type, 'some_string': str })
print(my_class)

# Or import all objects
objs = ultraimport('__dir__/../cherry.py', '*')
print(objs['MyClass'])

# Or them to our local scope
ultraimport('__dir__/../cherry.py', '*', globals=locals())
print(MyClass, '\n')

# The next import would fail because the imported banana.py contains a
# relative import in line 1: `from .. import cherry as relatively_imported_cherry`.
try: banana = ultraimport('__dir__/../yellow/banana.py')
except Exception as e: print('Catched import error: ', type(e), '\n')

# You have two options:
# Put banana.py it in a virtual namespace package using the last 2 folder parts,
# in this case `quickstart.yellow` to make it work
banana = ultraimport('__dir__/../yellow/banana.py', package=2)
print(banana, '\n', dir(banana), '\n')

# The subsequent relative import works:
print(banana.relatively_imported_cherry, '\n')

# Import cherry.py and put it in a virtual namespace package called `fruit`
# The fruit package is created automatically if it does not exist and the __path__
# is set to the parent folder, in this case `red`.
cherry = ultraimport('__dir__/../red/cherry.py', package='fruit')
print(cherry, '\n', dir(cherry), '\n')

# After creating the `fruit` namespace package as a side effect of the import,
# we can use it to do classical imports; remember the __path__ of `fruit` points to `red`
from fruit.strawberry import Strawberry
print(Strawberry, '\n', dir(Strawberry), '\n')

# You could also explicitly and dynamically create a virtual namespace pointing to the directory 'yellow'
yellow_ns = ultraimport.create_ns_package('yellow', '__dir__/../yellow')
print(yellow_ns, '\n', yellow_ns.__path__, '\n')

# For further imports, you must use the package_name `yellow` as provided as the first argument
from yellow import lemon
print(lemon, '\n', dir(lemon), '\n')

# Let's add some other module from a different directory to our virtual package
ultraimport('__dir__/../red/cherry.py', package='yellow')

from yellow.cherry import Cherry
print(Cherry)
