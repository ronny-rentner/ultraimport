#!/usr/bin/env python3

# Set to the parent directory of ultraimport (hopefully the last time you need to hack the sys.path)
sys.path.insert(0, '/home/ronny/Projects/py')
import ultraimport

ultraimport('__dir__/log.py', 'logger', globals=globals())

store, load = ultraimport('__dir__/cache.py', ('store', 'load'))

def main():
    # do something

    logger('I did something')

if __name__ == '__main__':
    main()

