print('submodule start', __package__, __name__)

ultraimport('__dir__/../xmodule.py', recurse=True)

from .. import xmodule
from . import siblingmodule

from ..mymodule import myfunction

myfunction('hello from submodule.py')

print('submodule end')
