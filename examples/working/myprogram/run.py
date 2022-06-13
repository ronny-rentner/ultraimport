#!/usr/bin/env python3


#
# Note 1: The following hack to adjust sys.path is only necessary for demo purposes so you can
#         just git clone the ultraimport repository and run this example without installation.
#
# Note 2: In real life, you'll install ultraimport as a (system wide or in your virtual environment)
#         library and you can then use the normal import feature of Python.

import sys, os
# Add the 4th parent directory of this example to sys.path
sys.path.insert(0, os.path.dirname(__file__) + '/../../..')


# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where run.py is in.
ultraimport('__dir__/log.py', 'logger', globals=globals())

# Lazy import the cache module. On the first access to any attribute of
# cache, the real cache module will be loaded
cache = ultraimport('__dir__/cache.py', lazy=True)

def main():
    # do something

    logger('I did something')

    cache.store('Something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
