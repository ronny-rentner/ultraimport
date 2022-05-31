#!/usr/bin/env python3


#
# Note 1: The following hack to adjust sys.path is only necessary for demo purpose so you can
#         just git clone the ultraimport repository and run this example without installation.
#
# Note 2: In real life, you'll install ultraimport as a system wide library and you can then
#         use the normal import feature of Python.

import sys, os
# Add the 4th parent directory of this example to sys.path
sys.path.insert(0, os.path.dirname(__file__) + '/../../../..')





import ultraimport

# `__dir__` refers to the directory where log.py is in
ultraimport('__dir__/log.py', 'logger', globals=globals())

# Alias objects after import
store, load = ultraimport('__dir__/cache.py', ('store', 'load'))

def main():
    # do something

    logger('I did something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
