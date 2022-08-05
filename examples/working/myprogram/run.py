#!/usr/bin/env python3

# ultraimport needs to be installed and imported in the classical way.
import ultraimport

# Import the 'logger' object from 'log.py' that is located in the same
# directory as this file and add 'logger' to the global namespace.
# `__dir__` refers to the directory where this file is in.
ultraimport('__dir__/log.py', 'logger', globals=globals())

def main():
    # do something
    logger('I did something')

if __name__ == '__main__':
    main()
else:
    logger('I was imported')
