from .log import logger

data = []

def store(value):
    if not value.startswith('cache'):
        logger('cache store: ' + value)
    data.append(value)

def load(value):
    if value in data:
        if not value.startswith('cache'):
            logger('cache load: ' + value)

        return value

    return None

