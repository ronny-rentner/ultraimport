import ultraimport

lib = ultraimport('__dir__/lib/lib.py', package=3)

print(lib)

import sys
print(sys.modules[lib.__package__])

