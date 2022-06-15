#!/usr/bin/env python3

# NOTE: Uncomment the following two lines of code to run this example without installing ultraimport.
#       Changing sys.path is only necessary for demo purposes so you can just git clone the repository
#       and directly run this example without installation.
#       In real life, you'll install ultraimport as a system wide library and you can then use the
#       normal import feature of Python without changing sys.path.

#import sys, os
#sys.path.insert(0, os.path.dirname(__file__) + '/../../..')




# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where this file is in.
ultraimport('__dir__/log.py', 'logger', globals=globals())

# Lazy import the cache module. On the first access to any attribute of the module,
# the real cache module will be loaded
cache = ultraimport('__dir__/cache.py', lazy=True)

def main():
    # do something

    logger('I did something')

    cache.store('Something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
