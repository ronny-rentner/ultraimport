#!/usr/bin/env python3

import ultraimport

lib = ultraimport('__dir__/lib/lib.py', package=2)

print(lib)

import sys
print(sys.modules[lib.__package__])

