#!/usr/bin/env python3

# Add the parent directory of ultraimport to sys.path.
#
# Note 1: The following hack to adjust sys.path is only necessary for demo purpose so you can
#         just git clone the ultraimport repository and run this example.
# Note 2: In real life, you'll install ultraimport as a system wide library and you can then
#         use the normal import feature of Python.

import sys, os
sys.path.insert(0, os.path.dirname(__file__) + '/../../..')





# From now on, we can do file based imports as long as we know the file name.
import ultraimport

# `__dir__` refers to the parent directory of the file with the calling function, so this file.
# You could also construct a path realtive to the current working yourself using
# `pathlib.Path(__file__).parent` or relative to your current working directory by using `./log.py`
#
# The logger object will be imported from log.py and it will be added to the globals.
ultraimport('__dir__/log.py', 'logger', globals=globals())

# Example of importing two functions from the cache module and assinging aliasses to them.
store, load = ultraimport('__dir__/cache.py', ('store', 'load'))

def main():
    # do something

    logger('I did something')

if __name__ == '__main__':
    main()

