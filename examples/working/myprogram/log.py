import ultraimport, sys

print("hello from log")

cache_load, cache_store = ultraimport('__dir__/cache.py', ['load', 'store'])

def logger(message):
    if not cache_load(message):
        print(message)
        cache_store(message)
    else:
        print('Not repeating message')


#logger("Logger fully loaded")
