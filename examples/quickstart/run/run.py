#!/usr/bin/env python3

#
# ultraimport - Quickstart Examples
#
# See https://github.com/ronny-rentner/ultraimport/#quickstart for more details on each example.
#

import ultraimport

def print_result(example, obj, obj_dir=None):
    """ Helper function to print results. """
    if not obj_dir:
        obj_dir = [ i for i in dir(obj) if not i.startswith('__') ]
    print(f"\nExample {example})\n{obj}\n{obj_dir}\n")


### 1) Import from parent folder
cherry = ultraimport('__dir__/../cherry.py')
print_result(1, cherry)


### 2) Import from sibling folder
other_cherry = ultraimport('__dir__/../red/cherry.py')
print_result(2, other_cherry)


### 3) Import single object
# Import the `Cherry` object from cherry.py and alias it to the name `my_class`
my_class = ultraimport('__dir__/../red/cherry.py', 'Cherry')
print_result(3, my_class)


### 4) Ensure type of imported object
my_class, my_string = ultraimport('__dir__/../cherry.py', { 'MyClass': type, 'some_string': str })
print_result(4, my_class, my_string)


### 5) Import all objects
objs = ultraimport('__dir__/../cherry.py', '*')
print_result(5, objs['MyClass'])


### 6) Add imported objects to a namespace
ultraimport('__dir__/../cherry.py', '*', add_to_ns=locals())
print_result(6, MyClass)


### 7) Give imported module a known parent package
try:
    banana = ultraimport('__dir__/../yellow/banana.py')
except Exception as e:
    print_result(7, e.__class__, e.file_path_resolved)


banana = ultraimport('__dir__/../yellow/banana.py', package=2)
print_result(7, banana, banana.relatively_imported_cherry)


### 8) Embed module in a virtual namespace package
cherry = ultraimport('__dir__/../red/cherry.py', package='some.fruit')
print_result(8, cherry)


### 9) Integrate with normal imports
from some.fruit.strawberry import Strawberry
print_result(9, Strawberry)


### 10) Create virtual namespace package
yellow_ns = ultraimport.create_ns_package('yellow', '__dir__/../yellow')
print_result(10, yellow_ns, yellow_ns.__path__)

from yellow import lemon
print_result(10, lemon)

ultraimport('__dir__/../red/cherry.py', package='yellow')
from yellow.cherry import Cherry
print_result(10, Cherry)

