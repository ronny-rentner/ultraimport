from .lib import lib

print(lib)

import sys
print(sys.modules[lib.__package__])
