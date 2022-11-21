import ultraimport

# Lazy load the logger by specifying the `objects_to_import` (2nd parameter)
# as a dict with the type as the value. This is necessary to resolve the cyclic
# dependency because the cache is using the logger and the logger is using the cache.
logger = ultraimport('__dir__/logging.py', {'logger': callable}, lazy=True)

data = []

def store(value):
    if not value.startswith('cache'):
        # Only when we actually try to log something through the logger() function,
        # the respective code in logging.py is actually loaded.
        logger('cache store: ' + value)
    data.append(value)

def load(value):
    if value in data:
        if not value.startswith('cache'):
            logger('cache load: ' + value)

        return value

    return None

