# Use:
#
# DEBUG=0 python ./run.py
#
# DEBUG=1 python ./run.py

import ultraimport

import re

def preprocess(source):

    print("Preprocessing..")

    # Here we use regular expressions to modify the source code but you can use
    # any other technique, e. g. a classical preprocessor like gpp or you could
    # use the ast module to parse and modify the AST.
    lines = []
    for line in source.decode().splitlines():
        # Wrap all lines starting with `log.debug(..` with `if DEBUG: log.debug(..`
        # so we skip calculation of any parameters
        line = re.sub('^(\s*)log\.debug\(', '\\1if DEBUG: log.debug(', line)
        lines.append(line)

    return str.join("\n", lines).encode()

debug = ultraimport('__dir__/debug.py', preprocessor=preprocess)

debug.main()
