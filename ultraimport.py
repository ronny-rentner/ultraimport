#
# ultraimport
#
# Get control over your imports -- no matter how you run your code.
#
# Copyright [2022] [Ronny Rentner] [ultraimport.code@ronny-rentner.de]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import importlib, importlib.machinery, importlib.util
import ast, collections, contextlib, inspect, os, pathlib, sys, types, traceback, time

# If possible, let's print nice exceptions via rich
try:
    from rich.traceback import install
    install(show_locals=False)
except:
    pass

__all__ = ['ultraimport']

# Needed for code transformation
if not hasattr(ast, 'unparse'):
    import astor
    ast.unparse = astor.to_source

# Needed for debug output
try: import astprettier
except: pass

# Keep track of reload count
""" Keep track """
reload_counter = 0
""" Keep track """

# Dict of loaded files, the keys are tuples of two
# input parameters of the ultraimport() function: file_path and the package parameter
cache = {}

# Keep track of ongoing imports to detect circular imports
import_ongoing_stack = {}

# Print debug output, especially for code transformation
debug = False
#debug = True

def ultraimport(file_path, objects_to_import=None, add_to_ns=None, preprocessor=None, package=None, caller=None, caller_reference=None,
                use_cache=True, lazy=False, recurse=False, inject=None, use_preprocessor_cache=True, cache_path_prefix=None):
    """
    Import Python code files from the file system. This is the central main function of ultraimport.

    Parameters:
        file_path (str): Path to the module file that should be imported. It can have any file extension. Please be
            aware that you must provide the file extension. The path can be relative or absolute. You can use the
            special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current
            working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some
            CPU cycles) you might want to set `caller=__file__`.

        objects_to_import (str | (Iterable[str] | Dict[str, object]): Can have several modes depending on the type of
            the parameter.
        - (str): Name of a single object to import from the module in `file_path`. The special value `'*'`
            selects all objects from that module.
        - (Iterable[str]): A list of names of objects to import.
        - (Dict[str, object]): The keys represent the names of the objects to import. The values define
            the expected types of those objects. A `TypeError` is thrown if the types don't match the
            expectation. If you set `lazy=True`, you must use a dict for `objects_to_import` and define the types.

        add_to_ns (Dict[str, object]): add the `objects_to_import` to the dict provided. Usually called with
            `add_to_ns=locals()` if you want the imported module to be added to the global namespace of the caller.

        preprocessor (callable): Takes the source code as an argument and can return a modified version of the source code.
            Check out the [debug-transform example](/examples/working/debug-transform) on how to use the preprocessor.

        package (str | int): Can have several modes depending on if you provide a string or an integer. If you provide
            a string, ultraimport will generate one or more namespace packages and use it as parent package of your
            imported module. If you set an integer, it means the number of path parts (directories) to extract from the
            `file_path` to calculate the namespace package. This can help with subsequent relative imports in your
            imported files. If `package` is set to the default `None`, the module will be imported without setting it
            parent `__package__`.

        caller (str): Can be set `caller=__file__` to save some CPU cycles. Otherwise it will be derived from the current
            stack.

        caller_reference (str): Used internally for error handling of lazy loading. It contains the file name of the
            caller and the line number separated by a colon.

        use_cache (bool): If set to `False`, allows re-importing of the same source file even if it was imported before.
            Otherwise a cached version of the imported module is returned.

        lazy (bool): *Experimental* *wip* If set to `True` and if `objects_to_import` is set to `None`, it will lazy
            import the module. If set to True and `objects_to_import` is a dict, the values of the dict must be the
            type of the object to lazy import from the module. Currently only the type `callable` is supported.

        recurse (bool): If set to `True`, a built-in preprocessor is activated to transparently rewrite all relative
            import statements (those with a dot like `from . import something`) to ultraimport() calls. Use this mode
            if you have no control over the source code of the impored modules.

        use_preprocessor_cache (bool): If set to `False`, the built-in preprocessor will not use any cache and always
            recompile (preprocess) all code files. This is useful for debugging.

        cache_path_prefix (str): Directory for storing preprocessed files. If you use the preprocessor feature or if
            you use the option `recurse=True` (which in turn uses the preprocessor feature) you will have the option to
            store the resulting code after preprocessing. By default, they are stored in parallel to the original
            source code files, but this option allows to override to location. One common setting is
            `cache_path_prefix='__pycache__'` to store the processed files along with the bytecode files.
            _Note_: Even when you change this directory, this will be hidden from Python. Towards Python, the
            preprocessed files will always look like they are in the same directory as the original source code files,
            even if they are not.

    Returns:
        Depending on the parameters *returns one of the following*:

        object: If `objects_to_import` is `None`, returns a single module object.

        object: If `objects_to_import` is a `str`, returns the single object with the specified name from the imported module.

        dict: If `objects_to_import` has the value `'*'`, returns a dict of all items from the imported module.

        list: If `objects_to_import` is a `List[str]`, return a list of imported objects from the imported module.

    """

    if debug:
        print("ultraimport", file_path)

    file_path_orig = file_path

    # If we are in Cython compiled code, there are not frames for what happens inside ultraimport
    if __file__.endswith('.so') or __file__.endswith('.pyx'):
        caller_level = 0

    frame = None

    if not caller or (add_to_ns == True) or lazy:
        caller, frame = find_caller(return_frame=True)

    if add_to_ns == True:
        if frame:
            add_to_ns = frame.f_locals
        else:
            raise Exception('No frame found to inject imported objects')

    if '__dir__' in file_path:
        file_path = file_path.replace('__dir__', os.path.dirname(caller))

    file_path = os.path.abspath(file_path)

    if lazy and (type(objects_to_import) == dict):

        if not caller_reference:
            caller_reference = f"{frame.f_code.co_filename}:{frame.f_lineno}"

        # Lazy load the whole module
        if not objects_to_import:
            importer = lambda: ultraimport(file_path_orig, caller=caller, caller_reference=caller_reference, use_cache=use_cache)
            name = get_module_name(file_path)
            module = LazyModule(name, file_path, importer=importer)
            sys.modules[name] = module
            return module

        # Lazy load individual objects from the module
        if type(objects_to_import) == dict:
            # Construct lambda function that allows to load the desired file later on
            importer = lambda: ultraimport(file_path_orig, caller=caller, caller_reference=caller_reference, use_cache=use_cache)
            for item, item_type in objects_to_import.items():
                if item_type == callable:
                    objects_to_import[item] = LazyCallable(importer=importer, callable_name=item)
                else:
                    raise Exception("Only types 'callable' and 'module' are supported")

            if add_to_ns:
                add_to_ns.update(objects_to_import)

            if len(objects_to_import) == 1:
                return list(objects_to_import.values())[0]

            return list(objects_to_import.values())
        else:
            raise Exception("When setting lazy=True the parameter objects_to_import must be a dict.")

    if file_path in import_ongoing_stack:
        # TODO: Come up with better error message how to handle circular import errors
        raise CircularImportError(file_path=file_path_orig, file_path_resolved=file_path)

    with contextlib.ExitStack() as cleaner:
        cleaner.callback(import_ongoing_stack.pop, file_path, None)

        import_ongoing_stack[file_path] = True


        #print('CACHE CHECK', use_cache, file_path, file_path in cache)
        #print('CACHE', cache)

        cache_key = (file_path, package)

        # TODO: Should we use resolved file_path for the cache?
        if use_cache and cache_key in cache:
            module = cache[cache_key]
        else:
            check_file_is_importable(file_path, file_path_orig, caller_reference)
            name = get_module_name(file_path)

            # If we want to recruse, we need to add our recurse preprocessor
            # to any other preprocessors from the user
            preprocessor_combined = preprocessor
            if recurse:
                def _(source, *args, **kwargs):
                    if preprocessor:
                        source = preprocessor(source, *args, **kwargs)
                    return RewriteImport.transform_imports(source, *args, **kwargs)
                preprocessor_combined = _

            package_name, package_path, package_module = get_package_name(file_path, package)

            # Long name of the module including parent package if available
            full_name = f'{package_name}.{name}' if package_name else name

            loader = Loader(full_name, file_path, preprocessor=preprocessor_combined, use_cache=use_preprocessor_cache, cache_path_prefix=cache_path_prefix)
            spec = importlib.util.spec_from_loader(full_name, loader)

            module = importlib.util.module_from_spec(spec)

            # Inject ultraimport module
            module.ultraimport = sys.modules[__name__]

            # Inject other dependencies
            if inject:
                for k, v in inject.items():
                    setattr(module, k, v)

            #print('__package__', package_name)
            #print('__path__', package_path)
            #print('module', module)
            if package_name:
                module.__package__ = package_name
                # Inject module into the package
                setattr(package_module, name, module)

            sys.modules[name] = module
            if use_cache:
                cache[cache_key] = module

            try:
                spec.loader.exec_module(module)
            except ImportError as e:
                # If the import fails, we do not cache the module
                if cache_key in cache:
                    del cache[cache_key]
                if name in sys.modules:
                    del sys.modules[name]

                # TODO: Move all the error case handling to the exception classes directly
                #print(e.msg, e.name, e.path)
                if (e.msg == 'attempted relative import with no known parent package' or
                    e.msg == 'attempted relative import beyond top-level package'):
                    if recurse:
                        raise ImportError('This is an internal ultraimport error. Please report this bug and the circumstances!')
                    if package:
                        raise ExecuteImportError('Wrongly handled, relative import statement found.', file_path=file_path_orig, file_path_resolved=file_path, from_exception=e).with_traceback(e.__traceback__) from None
                    else:
                        raise ExecuteImportError('Unhandled, relative import statement found.', file_path=file_path_orig, file_path_resolved=file_path, from_exception=e).with_traceback(e.__traceback__) from None
                if (e.msg.startswith('cannot import name') and e.msg.endswith('(unknown location)')):
                        raise ExecuteImportError(str(e), file_path=file_path_orig, file_path_resolved=file_path, from_exception=e).with_traceback(e.__traceback__) from None
                else:
                    raise e

        if objects_to_import:
            return_single = False
            return_zipped = False
            if objects_to_import == '*':
                objects_to_import = [ item for item in dir(module) if not item.startswith('__') ]
                return_zipped = True
            elif type(objects_to_import) == str:
                objects_to_import = [ objects_to_import ]
                return_single = True

            values = []
            for item in objects_to_import:
                try:
                    attr = getattr(module, item)
                    # When it's a dict, we expect the types of the imports to be the values
                    if (type(objects_to_import) == dict):
                        if not isinstance(attr, objects_to_import[item]):
                            raise TypeError(f"Import type mismatch, expected '{item}' to be of type {objects_to_import[item]} but got {type(attr)}")
                    values.append(getattr(module, item))
                except AttributeError as e:
                    raise ResolveImportError(str(e), file_path=file_path_orig, file_path_resolved=file_path) from None

            if add_to_ns or return_zipped:
                zipped = dict(zip(objects_to_import, values))

            if add_to_ns:
                add_to_ns.update(zipped)

            if return_single:
                return values[0]

            if return_zipped:
                return zipped

            return values
        # If there are no `objects_to_import`, it means we should import the whole module.
        # If `add_to_ns` is set, we must add it to this namespace.
        # TODO: Check that add_to_ns can take key/value pairs.
        elif add_to_ns:
            add_to_ns[module.__name__] = module

        if debug:
            print('module:', module)

        return module

##################
# ERROR HANDLING #
##################

# TODO: Switch to internal Python code info object
CodeInfo = collections.namedtuple('CodeInfo', ['source', 'file_path', 'line', 'offset'])

class ErrorRendererMixin():
    """ Mixin for Exception classes with some helper functions, mainly for rendering data to console """

    def render_table(self, data):
        """
        Render a table for error output on console output.

        The tables are meant to always have to columns with labels in the first
        column and values in the second column.
        """

        assert type(data) == list
        column1_size = 2
        column2_size = 2

        # First we identify the column width
        for k, v in data:
            column1_size = max(column1_size, len(str(k)))
            column2_size = max(column2_size, len(str(v)))

        table_lines = [ f" {k:>{column1_size}} │ {v}" for k, v in data ]

        return '\n'.join(table_lines) + '\n'

    def render_header(self, headline, message):
        headline_border = '─' * len(headline)
        return f"""

┌─{headline_border}─┐
│ {headline} │
└─{headline_border}─┘

{message}
"""

    def render_suggestion(self, line1, line2):
        return f"\n ╲ {line1}\n ╱ {line2}\n"

    def find_frame(self, frames, depth=1):
        while True:
            try:
                frame = frames[0 - depth]
                depth += 1
                if frame.filename == __file__ or '<frozen importlib._bootstrap' in frame.filename:
                    continue
            except IndexError as exc:
                break
            return frame

class RewrittenImportError(ImportError, ErrorRendererMixin):
    def __init__(self, message='', combine=None, code_info=None, object_to_import=None, *args, **kwargs):

        super().__init__('')

        if combine and len(combine) > 0:
            for e in combine:
                if type(e) is not ResolveImportError:
                    raise AttributeError(f"Type of combined exceptions in 'combine' attribute must be 'ultraimport.Error', but it was '{type(e)}'")

        if not combine or (len(combine) < 1):
            raise AttributeError("Missing errors of rewritten imports in 'combine' attribute")

        error_table = []
        if code_info:
            if type(code_info) is not CodeInfo:
                code_info = CodeInfo(*code_info)

            error_table.extend([
                ('Original source file', f"'{code_info.file_path}', line {code_info.line}:{code_info.offset}"),
                ('Original source code', code_info.source),
            ])

        exc_type, exc_value, exc_traceback = sys.exc_info()
        frame = traceback.extract_tb(exc_traceback)[0]
        error_table.extend([
            ('Preprocessed source file', f"{frame.filename}:{frame.lineno}"),
        ])

        error_table.append(('Error details', f"Could not find resource '{object_to_import}' in any of the following files:"))
        for e in combine:
            error_table.append(('', f'- {e.file_path_resolved}'))
            error_table.append(('', f'  (Possible reason: {e.reason})'))

        header = self.render_header('Rewritten Import Error', 'A relative import statement was transparently rewritten and failed.')
        body = self.render_table(error_table)

        suggestion = self.render_suggestion('Check if the required package or module really exists in your file system.',
            'If you know the path but cannot change the import statement, use dependency injection to inject the resource.')

        self.msg = f"{header}\n{body}{suggestion}"

    def find_cause(self, tb=None, depth=0):
        frame = None
        while True:
            try:
                frame = sys._getframe(depth)
                depth += 1
                if frame.f_code.co_filename == __file__ or '<frozen importlib._bootstrap' in frame.f_code.co_filename:
                    continue
            except ValueError as exc:
                break
        return frame

class CircularImportError(ImportError, ErrorRendererMixin):
    def __init__(self, message=None, file_path=None, file_path_resolved=None, *args):

        super().__init__()

        header = self.render_header('Circular Import Error', 'An unresolved circular import was detected while importing a file.')

        error_table = []
        suggestion = ''

        #import pprint
        #pprint.pprint(traceback.extract_stack())

        frame = self.find_frame(frames=traceback.extract_stack())
        error_table.extend([
            ('Source file', f"{frame.filename}:{frame.lineno}"),
            ('Happend in', frame.name),
            ('Source code', frame.line),
            ('Import file_path', file_path),
            ('Resolved file_path', file_path_resolved),
        ])

        suggestion = self.render_suggestion('You can use the ultraimport() parameter `lazy=True` to resolve circular dependencies.',
            'This will only actually load imported modules and callables when they are used for the first time.')

        body = self.render_table(error_table)

        self.msg = f"{header}\n{body}{suggestion}"

class ExecuteImportError(ImportError, ErrorRendererMixin):
    def __init__(self, message=None, file_path=None, file_path_resolved=None, from_exception=None, depth=2, *args, **kwargs):

        super().__init__()

        # Save file_path for later analyzation
        self.file_path = file_path
        self.file_path_resolved = file_path_resolved
        # Store the original reason/message for later
        self.reason = message

        header = self.render_header('Execute Import Error', 'An import file could be found and read, but an error happened while executing it.')
        suggestion = ''

        frame = traceback.extract_tb(from_exception.__traceback__)[-1]
        error_table = [
            ('Source file', f"{frame.filename}:{frame.lineno}"),
            ('Happend in', frame.name),
            ('Source code', frame.line)
        ]

        if from_exception and from_exception.msg == 'attempted relative import with no known parent package':
            error_table.append(('Possible reason', 'A subsequent, relative import statement was found, but not handled.'))

            suggestion = self.render_suggestion('To handle the relative import from above, use the ultraimport() parameter `recurse=True`.',
                'This will activate automatic rewriting of subsequent, relative imports. Alternatively set `package=<int>` to create a virtual package.')
        if from_exception and from_exception.msg == 'attempted relative import beyond top-level package':
            error_table.append(('Possible reason', 'A subsequent, relative import statement was found, but not handled correctly.'))

            suggestion = self.render_suggestion('To handle the relative import from above, use the ultraimport() parameter `recurse=True`.',
                'This will activate automatic rewriting of subsequent, relative imports. Alternatively set `package=<int>` to create a virtual package.')

        error_table.append(('Original error', f'"{from_exception.msg}"'))
        body = self.render_table(error_table)

        self.msg = f"{header}\n{body}{suggestion}"

class ResolveImportError(ImportError, ErrorRendererMixin):
    def __init__(self, message=None, file_path=None, file_path_resolved=None, from_exception=None, caller_reference=None, *args, **kwargs):

        super().__init__()

        # Save file_path for later analyzation
        self.file_path = file_path
        self.file_path_resolved = file_path_resolved
        # Store the original reason/message for later
        self.reason = message

        header = self.render_header('Resolve Import Error', 'An import file could not be found or not be read.')

        #frame = traceback.extract_stack()
        #print('FRAMES', frame)
        frame = self.find_frame(frames=traceback.extract_stack())
        error_table = [
            ('Source file', f"{frame.filename}:{frame.lineno}"),
            ('Happend in', frame.name),
            ('Source code', frame.line),
            ('Import file_path', file_path),
            ('Resolved file_path', file_path_resolved),
            ('Possible reason', self.reason)
        ]

        if caller_reference:
            error_table.insert(0, ('Lazy loaded', caller_reference))
            error_table = [
                ('Source file', caller_reference),
                ('Lazy loading triggered', f"{frame.filename}:{frame.lineno}"),
                ('Happend in', frame.name),
                ('Source code', frame.line),
                ('Import file_path', file_path),
                ('Resolved file_path', file_path_resolved),
                ('Possible reason', self.reason)
            ]

        suggestion = ''
        if file_path_resolved and not file_path_resolved.endswith('.py'):
            maybe_path = file_path_resolved + '.py'
            if os.path.exists(maybe_path):
                suggestion = self.render_suggestion(f"Did you mean to import '{maybe_path}'?",
                    "You need to add the file extension '.py' to the file_path.")

        if not suggestion:
            suggestion = self.render_suggestion('Check the resolved `file_path` and find out why the file is not readable.',
                'Maybe you have a typo in the `file_path` or maybe the parent directory does not exist or is not readable?')

        body = self.render_table(error_table)

        self.msg = f"{header}\n{body}{suggestion}"


################
# LAZY LOADING #
################

class LazyCass():
    """ Lazily-loaded class that triggers module loading on access """

    # TODO: https://stackoverflow.com/questions/61942205/lazy-class-factory
    pass

class LazyCallable():
    """ Lazily-loaded callable that triggers module loading on access """
    def __init__(self, importer, callable_name):
        self._importer = importer
        self._callable_name = callable_name

    def __call__(self, *args, **kwargs):
        if not hasattr(self, '_callable'):
            imported_module = self._importer()
            self._callable = getattr(imported_module, self._callable_name)

        return self._callable(*args, **kwargs)

class LazyModule(types.ModuleType):
    """ Lazily-loaded module that triggers loading on attribute access """

    def __init__(self, name, file_path, importer):
        super().__init__(name)
        self._importer = importer
        self.__file__ = file_path

    def __getattr__(self, key):
        if key == '_module':
            self._module = self._importer()
            return self._module
        return self._module.__getattribute__(key)

###########
# LOADERS #
###########

class Loader:
    """ Loader factory that returns either SourceFileLoader or ExtensionFileLoader depending on file_path """
    def __new__(cls, name, file_path, *args, **kwargs):
        _, suffix = os.path.splitext(file_path)

        if suffix in importlib.machinery.EXTENSION_SUFFIXES:
            return ExtensionFileLoader(name, file_path)

        return SourceFileLoader(name, file_path, *args, **kwargs)

class ExtensionFileLoader(importlib.machinery.ExtensionFileLoader):
    pass

class SourceFileLoader(importlib.machinery.SourceFileLoader):
    """ Preprocessing Python source file loader """

    def __init__(self, name, file_path, preprocessor=None, use_cache=True, cache_path_prefix=None):
        # Note: It seems the module name here is not really used in Python internally
        super().__init__(name, file_path)
        self.preprocessor = preprocessor
        self.use_cache = use_cache
        self.cache_path_prefix = cache_path_prefix
        if self.preprocessor:
            self.check_preprocess(file_path)

    def check_preprocess(self, file_path):
        #print('CHECK FILE', file_path)
        file_name, file_extension = os.path.splitext(file_path)

        # This is the file_path we pretend to be loading, so it appears in stack traces
        self.preprocess_file_path_display = f"{file_name}__preprocessed__{file_extension}"

        dir_name, file_name = os.path.split(file_name)

        # Add cache prefix to dir_name
        if self.cache_path_prefix:
            if os.path.isabs(self.cache_path_prefix):
                dir_name = f"{self.cache_path_prefix}{os.sep}{dir_name}"
            else:
                dir_name = f"{dir_name}{os.sep}{self.cache_path_prefix}"

        # This is the file_path we are really loading
        self.preprocess_file_path = f"{dir_name}{os.sep}{file_name}__preprocessed__{file_extension}"

        # Check if preprocessed file is outdated, if yes, run the preprocessing again
        if self.use_cache and os.path.exists(self.preprocess_file_path):
            #print('CHECK CACHE STILL VALID?', file_path, self.preprocess_file_path)
            preprocessed = os.stat(self.preprocess_file_path)
            original = os.stat(file_path)
            if original.st_mtime > preprocessed.st_mtime:
                self.preprocess(file_path)
        else:
            self.preprocess(file_path)

    def ensure_dir(self, path):
        dir_name, _ = os.path.split(path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)

    def preprocess(self, file_path):
        #print('PREP', file_path, self.use_cache, time.time())
        self.code = self.get_data(file_path, direct=True)
        self.code = self.preprocessor(self.code, file_path=file_path)

        if not self.use_cache:
            if os.path.exists(self.preprocess_file_path):
                os.remove(self.preprocess_file_path)
            return

        self.ensure_dir(self.preprocess_file_path)

        # Write processed code back for caching
        with open(self.preprocess_file_path, 'wb') as f:
            f.write(f"# NOTE: This file was automatically generated from:\n# {file_path}\n# DO NOT CHANGE DIRECTLY! {time.time()}\n".encode())
            f.write(self.code.encode() if hasattr(self.code, 'encode') else self.code)

            #os.utime(self.preprocess_file_path, (original['mtime'], original['mtime']))

    def is_bytecode(self, file_path):
        return file_path[file_path.rindex("."):] in importlib.machinery.BYTECODE_SUFFIXES

    def path_stats(self, path):
        #print('STATS START', path)
        if not self.use_cache:
            #print('CACHE OFF')
            # Invalidate bytecode cache
            raise OSError
        else:
            if self.preprocessor:
                #print('PRE STATS', path, self.preprocess_file_path)
                return super().path_stats(self.preprocess_file_path)

            #print('STATS', path)
            return super().path_stats(path)

    def get_data(self, path, direct=False):
        _, suffix = os.path.splitext(path)
        #print('GET DATA', direct, self.preprocessor, path, suffix)

        # We are importing a bytecode file, so it should be direct
        if len(suffix) > 0 and suffix in importlib.machinery.BYTECODE_SUFFIXES:
            direct = True

        if not direct and self.preprocessor:
            if path == self.preprocess_file_path_display:
                path = self.preprocess_file_path
            if not os.path.exists(path):
                #print('GET PREP CODE', path)
                return self.code
        #print('GET DIRECT')
        return super().get_data(path)

    def get_filename(self, fullname):
        if self.preprocessor:
            return self.preprocess_file_path_display
        return self.path

###########
# REWRITE #
###########

class RewriteImport(ast.NodeTransformer):

    def __init__(self, file_path=None, *args):
        super().__init__(*args)
        self.file_path = file_path

    @classmethod
    def transform_imports(cls, source, file_path=None, use_cache=True):

        tree = ast.parse(source)

        if debug:
            print('--IN--------')
            print(ast.dump(tree))
            astprettier.pprint(tree, show_offsets=False, ns_prefix='ast')
            print('---------')

        tree = ast.fix_missing_locations(cls(file_path=file_path).visit(tree))

        unparsed = ast.unparse(tree)

        if debug:
            print('--OUT--------')
            print(unparsed)
            print('---------')

        return unparsed.encode()


    def gen_try(self, try_body, except_body = ast.Pass(), except_alias = 'e', except_error = 'ultraimport.ResolveImportError'):
        if not except_body:
            except_body = ast.Pass()
        return ast.Try(
            body=[try_body],
            handlers=[
                ast.ExceptHandler(
                    type=ast.Name(id=except_error, ctx=ast.Load()),
                    name=except_alias,
                    body=[except_body],
                ),
            ],
            orelse=[],
            finalbody=[],
        )

    def gen_assign(self, targets, value):
        return ast.Assign(
            targets=targets,
            value=value
        )

    def gen_keyword(self, name, value):
        if isinstance(value, ast.Tuple) or isinstance(value, ast.Call):
            return ast.keyword(arg=name, value=value)
        return ast.keyword(arg=name, value=ast.Constant(value=value, kind=None))

    def gen_call(self, name, args=[], keywords=[]):
        return ast.Call(func=ast.Name(id=name, ctx=ast.Load()), args=args, keywords=keywords)

    def gen_import_call(self, file_path, import_elts=None):
        keywords = [
            self.gen_keyword('recurse', True),
            # TODO: Remove and use cache
            #self.gen_keyword('use_cache', False),
        ]

        if import_elts == '*':
            keywords.append(self.gen_keyword('add_to_ns', self.gen_call('add_to_ns')))

        return ast.Call(
            func=ast.Name(id='ultraimport', ctx=ast.Load()),
            args=[
                ast.Constant(value=file_path, kind=None),
                self.gen_keyword('objects_to_import', import_elts)
            ],
            keywords=keywords
        )

    def gen_code_info(self, source, file_path, line, offset):
        return ast.Tuple(elts=[
                ast.Constant(value=source, kind=None),
                ast.Constant(value=file_path, kind=None),
                ast.Constant(value=line, kind=None),
                ast.Constant(value=offset, kind=None),
            ],
            ctx=ast.Load(),
        )

    def gen_raise(self, alias, code_info, combine, object_to_import):
        return ast.Raise(
            exc=ast.Call(
                func=ast.Name(id='ultraimport.RewrittenImportError', ctx=ast.Load()),
                #args=[ast.Constant(value=message, kind=None)],
                args=[],
                keywords=[
                    self.gen_keyword('code_info', code_info),
                    self.gen_keyword('object_to_import', object_to_import),
                    ast.keyword(
                        arg='combine',
                        value=ast.List(
                            elts=[ ast.Name(id=name, ctx=ast.Load()) for name in combine ],
                            ctx=ast.Load(),
                        ),
                    ),
                ],
            ),
            #cause=None,
            cause=ast.Constant(value=None, kind=None),
        )

    def gen_import(self, alias, module_path, object_name=None):
        if object_name == '*':
            return self.gen_import_call(module_path, object_name)
        elif object_name:
            objects_tuple = self.gen_objects_tuple([object_name])
            aliasses_tuple = self.gen_aliasses_tuple([alias])
            call_node = self.gen_import_call(module_path, objects_tuple)
            return self.gen_assign([aliasses_tuple], call_node)

        call_node = self.gen_import_call(module_path)
        assign_node = self.gen_assign([ast.Name(id=alias, ctx=ast.Store())], call_node)
        return assign_node

    def gen_aliasses_tuple(self, aliasses):
        return ast.Tuple(elts=[ ast.Name(id=alias, ctx=ast.Store()) for alias in aliasses ], ctx=ast.Store())

    def gen_objects_tuple(self, object_names):
        if not object_names:
            return None
        return ast.Tuple(elts=[ast.Constant(value=name) for name in object_names], ctx=ast.Load())

    def visit_ImportFrom(self, node):
        """ Rewrite all `import .. from` statements """

        node = self.generic_visit(node)

        #code = ast.unparse(node)
        #print('NODE CODE:', code)

        ####
        # For imports with "from . import something"
        ####

        imports = []
        up = (node.level - 1) * f'..{os.sep}'

        for n in node.names:
            name = n.name if not node.module else node.module
            module_path = f"__dir__/{up}__init__.py"
            module2_path = f"__dir__/{up}{name}/__init__.py"
            module3_path = f"__dir__/{up}{name}.py"
            alias = n.asname if n.asname else n.name

            try_node = None

            code_info = self.gen_code_info(source=ast.unparse(node), file_path=self.file_path, line=node.lineno, offset=node.col_offset)

            if node.module:
                import1_node = self.gen_import(alias, module2_path, n.name)
                import2_node = self.gen_import(alias, module3_path, n.name)
                raise_node = self.gen_raise(name, combine=['e', 'e2'], code_info=code_info, object_to_import=n.name)
                try2_node = self.gen_try(import2_node, raise_node, 'e2')
                try_node = self.gen_try(import1_node, try2_node, 'e')

            else:
                import1_node = self.gen_import(alias, module_path, name)
                import2_node = self.gen_import(alias, module2_path, name)
                import3_node = self.gen_import(alias, module3_path)
                raise_node = self.gen_raise(name, combine=['e', 'e2', 'e3'], code_info=code_info, object_to_import=name)
                try3_node = self.gen_try(import3_node, raise_node, 'e3')
                try2_node = self.gen_try(import2_node, try3_node, 'e2')
                try_node = self.gen_try(import1_node, try2_node, 'e')

            imports.append(try_node)
            ast.copy_location(try_node, node)

        return imports

##########
# HELPER #
##########

def get_module_name(file_path):
    """
    Return Python compatible module name from file_path. Replace dash and dot characters with underscore characters.

    Parameters:
        file_path (str): File path to a module or directory path to a package

    Returns:
        module_name (str): Extracted and escaped name of the module
    """

    # Try Python internal approach first
    name = inspect.getmodulename(file_path)

    # If Python cannot determine a name, we will simply split off any file extensions
    if not name:
        name, suffix = os.path.splitext(os.path.basename(file_path))

    # And replace all illegal characters
    return name.replace('-', '_').replace('.', '_')

def get_package_name(file_path, package):
    """
    Generate necessary package hierarchy according to the `package` parameter and
    create virtual namespace packages accordingly.

    Parameters:
        file_path (str): File path to a module or directory path to a package
        package (str): Provide package name as a string. Can contain multiple parts separated by dots.
                       The `__path__` of the package will be set to the parent directory of `file_path`.
        package (int): Derive package name from the parent directory name(s) of `file_path` using <package> number
                       of parent directories.

    Returns:
        A tuple containing

        package_name (str): Name of the package
        package_path (str): Path to the package
        package_module (types.ModuleType): Package module object
    """
    path = os.path.abspath(file_path if os.path.isdir(file_path) else os.path.dirname(file_path))
    if type(package) == str:
        rest, dot, name = package.rpartition('.')
        parent_package = None
        if rest:
            parent_package = get_package_name(os.path.dirname(file_path), rest)
        package_module = create_ns_package(package, path)
        if parent_package:
            package_module.__package__ = parent_package
        return package, path, package_module
    elif type(package) == int:
        pathes = os.path.dirname(os.path.abspath(file_path)).split(os.sep)[-package:]
        package = '.'.join(pathes)
        return get_package_name(path, package)
    return None, None, None

def find_caller(return_frame=False):
    """
    Find out who is calling by looking at the stack and searching for the first external frame.

    Parameters:
        return_frame (bool): If True, also return the stack frame.

    Returns:
        Depending on the parameters returns *one* of the following:

        str: A string with the caller name
        str, frame: A string with the caller name, the stack frame that was used to extract the caller name
    """

    frame = inspect.currentframe()

    # Note: If we run a compiled ultraimport module from Python REPL, there will only be one frame
    #       on the stack called <stdin>, and there will be no ultraimport frame, so __do not__ go back
    #       one frame automatically.
    #frame = frame.f_back

    while frame:
        if frame.f_code.co_filename != __file__:
            break
        frame = frame.f_back

    caller = frame.f_code.co_filename

    # If we are being used from a compiled module, we need to do
    # some more steps to extract the file name of the compiled module
    if caller == '<frozen importlib._bootstrap>':
        if 'args' in frame.f_locals and len(frame.f_locals['args']) > 0:
            caller = frame.f_locals['args'][0].__file__
        else:
            raise Exception('Cannot extract file name from caller. Please report this issue. In the meantime, you can use  when using ultraimport(..., caller=__file__)')

    if caller == '<stdin>':
        caller = f"{os.getcwd()}{os.sep}<stdin>"

    if return_frame:
        return caller, frame

    del frame

    return caller

def create_ns_package(package_name, package_path, caller=None):
    """
    Create one or more dynamic namespace packages on the fly.

    Parameters:
        package_name (str): Name of the namespace package that should be created.

        package_path (str): File system path of a directory that should be associated with the package.
            You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python
            REPL, the current working directory will be used for `__dir__`.

        caller (str): File system path to the file of the calling module. If you use advanced debugging tools
            (or want to save some CPU cycles) you might want to set `caller=__file__`. Otherwise the caller
            is derrived from the frame stack.
    """

    if '__dir__' in package_path:
        if not caller:
            caller = find_caller()
        package_path = os.path.abspath(package_path.replace('__dir__', os.path.dirname(caller)))

    rest, dot, name = package_name.rpartition('.')
    # Make sure to create parent package first
    if rest:
        create_ns_package(rest, os.path.dirname(package_path), caller=caller)

    loader = importlib._bootstrap_external._NamespaceLoader('loader', [package_path], None)
    spec = importlib.util.spec_from_loader(package_name, loader)
    package = importlib.util.module_from_spec(spec)
    package.__path__ = loader._path
    sys.modules[package_name] = package
    return package

def find_existing_module_by_path(file_path):
    for name, module in sys.modules.items():
        if module.__file__ == os.path.abspath(file_path):
            return module

    return None

def check_file_is_importable(file_path, file_path_orig, caller_reference=None):
    if not os.path.exists(file_path):
        raise ResolveImportError('File does not exist.', file_path=file_path_orig,
                                 file_path_resolved=file_path, caller_reference=caller_reference)

    if not os.path.isfile(file_path):
        raise ResolveImportError('Object exists but is not a file.', file_path=file_path_orig,
                                 file_path_resolved=file_path, caller_reference=caller_reference)

    if not os.access(file_path, os.R_OK):
        raise ResolveImportError('File exists but no read access.', file_path=file_path_orig,
                                 file_path_resolved=file_path, caller_reference=caller_reference)

    return True

def reload(ns=None, add_to_ns=True):
    """ Reload ultraimport module """
    count = reload_counter
    reloaded = importlib.reload(sys.modules[__name__])
    reloaded.reload_counter = count + 1
    reloaded.cache = {}

    return reloaded

class CallableModule(types.ModuleType):
    """ Makes ultraimport directly callable after doing `import ultraimport` """
    def __call__(self, *args, **kwargs):
        return ultraimport(*args, **kwargs)

sys.modules[__name__].__class__ = CallableModule
__path__ = os.path.dirname(__file__)
