#from . import log, other as real_other
#from .logger import   log as log2, log2 as log3 # Yes
#from . import log, log2, log3 # test
#from .log import *

from . import log, other_logger as log2

print('Message from mymodule.py:\n', 'log:', log, '\n', 'log2:', log2)

