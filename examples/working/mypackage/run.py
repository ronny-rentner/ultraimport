
#from somepackage.subpackage import submodule

import ultraimport
#submodule = ultraimport('__dir__/somepackage/subpackage/submodule.py', package=3)

submodule = ultraimport('__dir__/somepackage/subpackage/submodule.py', recurse=True)
