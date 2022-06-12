import ultraimport

import re

import dis

def preprocess(source):
    print("preprocess")
    lines = []
    for line in source.decode().splitlines():
        line = re.sub('^(\s*)log\.debug\(', '\\1if DEBUG: log.debug(', line)
        #re.sub
        print('x', line)
        lines.append(line)

    return str.join("\n", lines).encode()

debug = ultraimport('__dir__/debug.py', preprocessor=preprocess)

debug.main()
