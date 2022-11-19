#!/usr/bin/env python3

import ultraimport

def print_result(example, obj, obj_dir=None):
    """ Helper function to print results. """
    if not obj_dir:
        obj_dir = [ i for i in dir(obj) if not i.startswith('__') ]
    print(f"\nExample {example}:\n{obj}\n{obj_dir}\n")


# Example 1:
# Import Python module 'cherry.py' from parent folder
cherry = ultraimport('__dir__/../cherry.py')
print_result(1, cherry)


# Example 2:
# Import another Python module 'cherry.py' from a sibling folder
other_cherry = ultraimport('__dir__/../red/cherry.py')
print_result(2, other_cherry)


# Example 3:
# Import the `Cherry` object from cherry.py and alias it to the name `my_class`
my_class = ultraimport('__dir__/../red/cherry.py', 'Cherry')
print_result(3, my_class)


# Example 4:
# We can make sure my_class is actually the type we expect, a class,
# and my_string is a string, otherwise a TypeError is thrown.
my_class, my_string = ultraimport('__dir__/../cherry.py', { 'MyClass': type, 'some_string': str })
print_result(4, my_class, my_string)


# Example 5:
# Or import all objects
objs = ultraimport('__dir__/../cherry.py', '*')
print_result(5, objs['MyClass'])


# Example 6:
# Or them to our local scope
ultraimport('__dir__/../cherry.py', '*', add_to_ns=locals())
print_result(6, MyClass)


# Example 7:
# The next import would fail because the imported banana.py contains a
# relative import in line 1: `from .. import cherry as relatively_imported_cherry`.
try:
    banana = ultraimport('__dir__/../yellow/banana.py')
except Exception as e:
    print_result(7, e.__class__, e.file_path_resolved)


# Example 8:
# You have two options:
# Put banana.py it in a virtual namespace package using the last 2 folder parts,
# in this case `quickstart.yellow` to make it work.
banana = ultraimport('__dir__/../yellow/banana.py', package=2)
print_result(8, banana, banana.relatively_imported_cherry)
# By the way, the other option is more advanced by using recurse=True:
# This will rewrite any relative imports in your code dynamically to use ultraimport().


# Example 9:
# Import cherry.py and put it in a virtual namespace package called `fruit`
# The fruit package is created automatically if it does not exist and the __path__
# is set to the parent folder, in this case `red`.
cherry = ultraimport('__dir__/../red/cherry.py', package='some.fruit')
print_result(9, cherry)


# Example 10:
# After creating the `fruit` namespace package as a side effect of the import,
# we can use it to do classical imports; remember the __path__ of `fruit` points to `red`,
# the parent directory of the cherry.py module we have imported.
from some.fruit.strawberry import Strawberry
print_result(10, Strawberry)


# Example 11:
# You could also explicitly create a virtual namespace pointing to the directory 'yellow'
yellow_ns = ultraimport.create_ns_package('yellow', '__dir__/../yellow')
print_result(11, yellow_ns, yellow_ns.__path__)


# Example 12:
# For further imports, you must use the package_name `yellow` as provided as the first argument.
from yellow import lemon
print_result(12, lemon)


# Example 13:
# Let's add some other module from a different directory to our virtual package
ultraimport('__dir__/../red/cherry.py', package='yellow')
from yellow.cherry import Cherry
print_result(13, Cherry)

