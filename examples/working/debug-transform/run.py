#!/usr/bin/env python3

# Use:
#
# DEBUG=0 python ./run.py
#
# DEBUG=1 python ./run.py


# NOTE: Uncomment the following two lines of code to run this example without installing ultraimport.
#       Changing sys.path is only necessary for demo purposes so you can just git clone the repository
#       and directly run this example without installation.
#       In real life, you'll install ultraimport as a system wide library and you can then use the
#       normal import feature of Python without changing sys.path.

#import sys, os
#sys.path.insert(0, os.path.dirname(__file__) + '/../../..')



# ultraimport needs to be installed and imported in the classical way.
import ultraimport
import re

def preprocess(source):
    print("Preprocessing...")

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

debug.debug()
