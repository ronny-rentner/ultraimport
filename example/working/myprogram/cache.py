data = {}

def store(key, value):
    logger('store', key, value)
    data[key] = value

def load(key):
    logger('load', key)
    return data[key]
