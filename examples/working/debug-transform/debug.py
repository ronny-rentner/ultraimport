import logging as log

import os, dis, timeit

DEBUG=False if os.environ.get('DEBUG', "0") in ['0', 'no', 'off', 'false', 'False'] else True
print('DEBUG:', DEBUG)

# If the DEBUG flag is set, we print our debug log messages.
if DEBUG:
    log.basicConfig(level=log.DEBUG)
# Otherwise we print only error messages and higher.
else:
    log.basicConfig(level=log.ERROR)

# Simulate expensive calculation result
def expensive_calculation():
    import time
    print('expensive calcualtion: sleeping 3 seconds now')
    time.sleep(3)
    return 'expensive'

# Classical approach how to optimize your debug prints when
# expensive calculations are invovled
def my_log(*args):
    if DEBUG:
        message = args[0]
        # Do the expensive calls only if DEBUG is actually turned on
        args = [arg() for arg in args[1:] if callable(arg)]
        log.debug(message, args)

def third():
    # This is fast but ugly. You have to pollute your code
    # with these if conditions all over the place
    if DEBUG: log.debug('Third debug print: %s', expensive_calculation())

def second():
    # This is looking better but more expensive and less
    # flexible and more code (and therefore more error prone)
    my_log('Second debug print: %s', expensive_calculation)

def first():
    # Without any optimization, the expensive calcualtion is done
    # even when we never actually print our log message
    log.debug('First debug print: %s', expensive_calculation())

def main():
    first()
    second()
    third()
    if not DEBUG:
        print('Production timings with no debug prints:')
        print('first()', min(timeit.repeat('first()', globals=globals())))
        print('second()', min(timeit.repeat('second()', globals=globals())))
        print('third()', min(timeit.repeat('third()', globals=globals())))

if __name__ == '__main__':
    main()
