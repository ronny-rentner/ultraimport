import ultraimport

# Import mymodule from mypackage and recursively rewrite all relative imports to use
# ultraimport() so they continue to work
mymodule = ultraimport('__dir__/mypackage/mymodule.py', recurse=True)
