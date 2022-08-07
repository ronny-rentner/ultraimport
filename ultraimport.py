#
# ultraimport
#
# Reliable, file system based imports -- no matter how you run your code
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
import ast, collections, os, sys, contextlib, types, traceback, time

try:
    from rich.traceback import install
    install(show_locals=False)
except:
    pass

__all__ = ['ultraimport']

if not hasattr(ast, 'unparse'):
    import astor
    ast.unparse = astor.to_source

try:
    import astprettier
except:
    pass

reload_counter = { 0: 0 }
cache = {}
import_ongoing_stack = {}

debug = False
#debug = True

##################
# ERROR HANDLING #
##################

CodeInfo = collections.namedtuple('CodeInfo', ['source', 'file_path', 'line', 'offset'])

class ErrorRendererMixin():

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

        return '\n'.join(table_lines)

    def render_header(self, headline, message):
        headline_border = '─' * len(headline)
        return f"""

┌─{headline_border}─┐
│ {headline} │
└─{headline_border}─┘

{message}
"""

    def render_suggestion(self, line1, line2):
        return f"\n\n ╲ {line1}\n ╱ {line2}\n"

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
    def __init__(self, message='', combine=None, code_info=None, object_to_import=None, *args):

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

        import pprint
        pprint.pprint(traceback.extract_stack())

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
    def __init__(self, message=None, file_path=None, file_path_resolved=None, from_exception=None, depth=2, *args):

        super().__init__()

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
            error_table.append(('Original errror', f'"{from_exception.msg}"'))

            suggestion = self.render_suggestion('To handle the relative import from above, use the ultraimport() parameter `recurse=True`.',
                'This will activate automatic rewriting of subsequent, relative imports.')

        body = self.render_table(error_table)

        self.msg = f"{header}\n{body}{suggestion}"

class ResolveImportError(ImportError, ErrorRendererMixin):
    def __init__(self, message=None, file_path=None, file_path_resolved=None, from_exception=None, *args):

        super().__init__()

        # Save file_path for later analyzation
        self.file_path = file_path
        self.file_path_resolved = file_path_resolved
        # Store the original reason/message for later
        self.reason = message

        header = self.render_header('Resolve Import Error', 'An import file could not be found or not be read.')

        error_table = [
            ('Import file_path', self.file_path),
            ('Resolved file_path', self.file_path_resolved),
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

class SourceFileLoader(importlib.machinery.SourceFileLoader):
    """ Preprocessing Python source file loader """

    def __init__(self, name, file_path, preprocessor=None, use_cache=True, cache_path_prefix=None):
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
            f.write(self.code)

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
            keywords.append(self.gen_keyword('globals', self.gen_call('globals')))

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


def get_module_name(file_path):
    """ Calculate Python compatible module name from file_path """
    base_name = os.path.basename(file_path)
    name, file_extension = os.path.splitext(base_name)
    return name.replace('-', '_').replace('.', '_')

def get_package_name(file_path, package):
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

def create_ns_package(package_name, package_path):
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

def check_file_is_importable(file_path, file_path_orig):
    if not os.path.exists(file_path):
        raise ResolveImportError('File does not exist.', file_path=file_path_orig, file_path_resolved=file_path)

    if not os.path.isfile(file_path):
        raise ResolveImportError('Object exists but is not a file.', file_path=file_path_orig, file_path_resolved=file_path)

    if not os.access(file_path, os.R_OK):
        raise ResolveImportError('File exists but no read access.', file_path=file_path_orig, file_path_resolved=file_path)

    return True

def ultraimport(file_path, objects_to_import=None, globals=None, preprocessor=None, package=None, caller=None, caller_level=1, use_cache=True, lazy=False, recurse=False, inject=None, use_preprocessor_cache=True, cache_path_prefix=None):
    if debug:
        print("ultraimport", file_path)

    if objects_to_import == '*' and globals == None:
        raise ValueError("Cannot import '*' without having globals set.")

    file_path_orig = file_path

    # We are supposed to replace the string `__dir__` in file_path with the directory of the caller.
    # If the caller is not provided via parameter, we'll find it out ourselves.
    if not caller:
        import inspect
        caller = inspect.stack()[caller_level].filename

    if caller == '<stdin>':
        caller = f"{os.getcwd()}{os.sep}<stdin>"

    if '__dir__' in file_path:
        file_path = file_path.replace('__dir__', os.path.dirname(caller))

    file_path = os.path.abspath(file_path)

    if lazy and (type(objects_to_import) == dict):
        # Lazy load the whole module
        if not objects_to_import:
            importer = lambda: ultraimport(file_path, caller=caller, use_cache=use_cache)
            name = get_module_name(file_path)
            module = LazyModule(name, file_path, importer=importer)
            sys.modules[name] = module
            return module

        # Lazy load individual objects from the module
        if type(objects_to_import) == dict:
            # Construct lambda function that allows to load the desired file later on
            importer = lambda: ultraimport(file_path, caller=caller, use_cache=use_cache)
            for item, item_type in objects_to_import.items():
                if item_type == callable:
                    objects_to_import[item] = LazyCallable(importer=importer, callable_name=item)
                else:
                    raise Exception("Only types 'callable' and 'module' are supported")

            if globals:
                globals.update(objects_to_import)

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

        # TODO: Should we use resolved file_path for the cache?
        if use_cache and file_path in cache:
            module = cache[file_path]
        else:

            check_file_is_importable(file_path, file_path_orig)
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

            loader = SourceFileLoader(name, file_path, preprocessor=preprocessor_combined, use_cache=use_preprocessor_cache, cache_path_prefix=cache_path_prefix)
            spec = importlib.util.spec_from_loader(name, loader)
            module = importlib.util.module_from_spec(spec)

            # Inject ultraimport module
            module.ultraimport = sys.modules[__name__]

            # Inject other dependencies
            if inject:
                for k, v in inject.items():
                    setattr(module, k, v)

            package_name, package_path, package_module = get_package_name(file_path, package)
            #print('__package__', package_name)
            #print('__path__', package_path)
            if package_name:
                module.__package__ = package_name
                setattr(package_module, __name__, module)

            sys.modules[name] = module
            if use_cache:
                cache[file_path] = module

            try:
                spec.loader.exec_module(module)
            except ImportError as e:
                # If the import fails, we do not cache the module
                if file_path in cache:
                    del cache[file_path]
                if name in sys.modules:
                    del sys.modules[name]

                #print(e.msg, e.name, e.path)
                if (e.msg == 'attempted relative import with no known parent package' or
                    e.msg == 'attempted relative import beyond top-level package'):
                    if recurse:
                        raise ImportError('This is an internal ultraimport error. Please report this bug and the circumstances!')
                    if package:
                        raise ImportError(f'ultraimport found an import ambiguity when importing {file_path}.\nYou need to either increase the level of package=int or, if that does not help, set recurse=True.')
                    else:
                        #e.msg = f'ultraimport found an import ambiguity when importing {file_path}.\nYou need to either set the level of package=int or, if that does not help, set recurse=True.'
                        raise ExecuteImportError('Unhandled, relative import statement found.', file_path=file_path_orig, file_path_resolved=file_path, from_exception=e).with_traceback(e.__traceback__) from None
                else:
                    raise e

        if objects_to_import:
            return_single = False
            if objects_to_import == '*':
                objects_to_import = [ item for item in dir(module) if not item.startswith('__') ]
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

            if globals:
                globals.update(zip(objects_to_import, values))

            if return_single:
                return values[0]

            return values
        elif globals:
            globals[module.__name__] = module

        if debug:
            print('module:', module)

        return module

def reload(globals=None):
    """ Reload ultraimport module """
    reload_counter[0] += 1
    reloaded = ultraimport(__file__, use_cache=False)
    CallableModule = reloaded.CallableModule
    cache = {}
    if globals and 'ultraimport' in globals:
        globals['ultraimport'] = reloaded
    return reloaded

# Make ultraimport() directly callable after doing `import ultraimport`
class CallableModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return ultraimport(*args, caller_level=2, **kwargs)

sys.modules[__name__].__class__ = CallableModule
