from .cache import load as cache_load, store as cache_store

def logger(message):
    if not cache_load(message):
        print(message)
        cache_store(message)
    else:
        print('Not repeating message')

