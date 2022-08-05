
# Note: other_logger does not exist, this is for testing the error case
#from . import log, other_logger as log2

from . import log, other as log2

print('Message from mymodule.py:\n', 'log:', log, '\n', 'log2:', log2)

