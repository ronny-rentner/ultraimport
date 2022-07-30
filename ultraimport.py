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
import ast, collections, os, sys, contextlib, types, traceback

try:
    import astprettier
except:
    pass

cache = {}
import_ongoing_stack = {}

#debug = True
debug = False

CodeInfo = collections.namedtuple('CodeInfo', ['source', 'file_path', 'line', 'offset'])

class RewrittenImportError(ImportError):
    def __init__(self, message='', combine=None, code_info=None, object_to_import=None, *args):

        if combine and len(combine) > 0:
            for e in combine:
                if type(e) is not Error:
                    raise AttributeError(f"Type of combined exceptions in 'combine' attribute must be 'ultraimport.Error', but it was '{type(e)}'")

        if not combine or (len(combine) < 1):
            raise AttributeError("Missing errors of rewritten imports in 'combine' attribute")

        message_code_info = ''
        if code_info:
            if type(code_info) is not CodeInfo:
                code_info = CodeInfo(*code_info)
            message_code_info = f"""
A relative import statement was transparently rewritten and failed.

Original file_path: '{code_info.file_path}', line {code_info.line}:{code_info.offset}
Original source code: '{code_info.source}'
"""

        files = '\n'.join(f' ● {e.file_path_resolved}\n   (reason: {e.reason})' for e in combine)
        message = f"""

┌────────────────────────┐
│ Rewritten Import Error │
└────────────────────────┘
{message_code_info}
When importing '{object_to_import}', it could not been found in any of the files:
{files}
"""

        super().__init__('')

        self.msg = message

class Error(ImportError):
    def __init__(self, message=None, file_path=None, file_path_resolved=None, *args):

        # Save file_path for later analyzation
        self.file_path = file_path
        self.file_path_resolved = file_path_resolved
        # Store the original reason/message for later
        self.reason = message

        suggestion = ""
        if file_path_resolved and not file_path_resolved.endswith('.py'):
            maybe_path = file_path_resolved + '.py'
            if os.path.exists(maybe_path):
                suggestion += f"\n ╲ Did you mean to import '{maybe_path}'?\n ╱ You need to add the file extension '.py' to the file_path."

        message = f"""

┌────────────────────┐
│ Ultra Import Error │
└────────────────────┘

Original file_path: '{self.file_path}'
Resolved file_path: {self.file_path_resolved}
                    (Possible reason: {self.reason})
{suggestion}
"""

        super().__init__('')

        self.msg = message

        # TODO: How to replace the original stack trace with ours?
        #if add_cause:
        #    print('ADD CAUSE: ', cause)
        #    self.__cause__ = cause if cause else self.build_cause()

    def build_cause(self):
        tb = None
        depth = 0
        while True:
            try:
                frame = sys._getframe(depth)
                depth += 1
                if frame.f_code.co_filename == __file__ or '<frozen importlib._bootstrap' in frame.f_code.co_filename:
                    continue
            except ValueError as exc:
                break

            tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)

        return Error(message=None, file_path=self.file_path, file_path_resolved=self.file_path_resolved,
                add_cause=False).with_traceback(tb)

    #def __repr__(self):
    #    return 'REPR'

    #def __str__(self):
    #    return 'STR'

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

    def __init__(self, name, file_path, preprocessor=None, cache=True, cache_path_prefix=''):
        super().__init__(name, file_path)
        self.preprocessor = preprocessor
        self.cache = cache
        self.cache_path_prefix = cache_path_prefix
        if self.preprocessor:
            self.check_preprocess(file_path)

    def check_preprocess(self, file_path):
        file_name, file_extension = os.path.splitext(file_path)

        # This is the file_path we pretend to be loading, so it appears in stack traces
        self.preprocess_file_path_display = f"{file_name}__preprocessed__{file_extension}"

        folder, file_name = os.path.split(file_name)
        # This is the file_path we are really loading
        self.preprocess_file_path = f"{sys.pycache_prefix or ''}{folder}{os.sep}__pycache__{os.sep}{file_name}__preprocessed__{file_extension}"

        if self.cache and os.path.exists(self.preprocess_file_path):
            #print('CHECK CACHE STILL VALID?', file_path, self.preprocess_file_path)
            preprocessed = os.stat(self.preprocess_file_path)
            original = os.stat(file_path)
            if original.st_mtime > preprocessed.st_mtime:
                self.preprocess(file_path)
        else:
            self.preprocess(file_path)

    def calculate_preprocess_file_pathes(self, file_path):
        dir_name, file_name = os.path.split(file_name)
        base_name, file_extension = os.path.splitext(file_name)

        # Add cache prefix to dir_name
        if self.cache_path_prefix:
            dir_name = f"{self.cache_path_prefix}{os.sep}{dir_name}" \
                if os.path.isabs(self.cache_path_prefix) \
                else f"{dir_name}{os.sep}{self.cache_path_prefix}"

        # Real, absolute, full path to cached, preprocessed file
        self.preprocess_file_path = f"{folder}{os.sep}{file_name}__preprocessed__{file_extension}"

        self.preprocess_file_path_display = self.preprocess_file_path

        self.preprocess_file_path_display = f"{base_name}__preprocessed__{file_extension}"

    def preprocess(self, file_path):
        #print('PREP', file_path)
        self.code = self.get_data(file_path, direct=True)
        self.code = self.preprocessor(self.code, file_path=file_path)
        # Write processed code back for caching
        with open(self.preprocess_file_path, 'wb') as f:
            f.write(f"# NOTE: This file was automatically generated from:\n# {file_path}\n# DO NOT CHANGE DIRECTLY!\n".encode())
            f.write(self.code)
        #os.utime(self.preprocess_file_path, (original['mtime'], original['mtime']))

    def is_bytecode(self, file_path):
        return file_path[file_path.rindex("."):] in importlib.machinery.BYTECODE_SUFFIXES

    def path_stats(self, path):
        #print('STATS START', path)
        if not self.cache:
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
        #print('GET DATA', direct, self.preprocessor, path)
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

    def gen_try(self, try_body, except_body = ast.Pass(), except_alias = 'e', except_error = 'ultraimport.Error'):
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
        if isinstance(value, ast.Tuple):
            return ast.keyword(arg=name, value=value)
        return ast.keyword(arg=name, value=ast.Constant(value=value, kind=None))

    def gen_import_call(self, file_path, import_elts=None):
        return ast.Call(
            func=ast.Name(id='ultraimport', ctx=ast.Load()),
            args=[
                ast.Constant(value=file_path, kind=None),
                self.gen_keyword('objects_to_import', import_elts)
            ],
            keywords=[
                self.gen_keyword('recurse', True),
                # TODO: Remove and use cache
                self.gen_keyword('use_cache', False),
            ],
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
        if object_name:
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


def transform_imports(source, file_path=None):

    tree = ast.parse(source)

    if debug:
        print('--IN--------')
        print(ast.dump(tree))
        astprettier.pprint(tree, show_offsets=False, ns_prefix='ast')
        print('---------')

    tree = ast.fix_missing_locations(RewriteImport(file_path=file_path).visit(tree))

    unparsed = ast.unparse(tree)

    if debug:
        print('--OUT--------')
        print(unparsed)
        print('---------')

    return unparsed.encode()

def get_module_name(file_path):
    """ Calculate Python compatible module name from file_path """
    base_name = os.path.basename(file_path)
    name, file_extension = os.path.splitext(base_name)
    return name.replace('-', '_').replace('.', '_')

def get_package_name(file_path, package):
    if type(package) == str:
        path = os.path.abspath(os.path.dirname(file_path))
        return package, path
    elif type(package) == int:
        path = os.path.abspath(os.path.dirname(file_path))
        package = '.'.join(os.path.dirname(os.path.abspath(file_path)).split(os.sep)[-package:])
        return package, path
    return None, None

def create_virtual_package(package_name, package_path):
    package = types.ModuleType(package_name)
    package.__package__ = package_name
    package.__path__ = [ package_path ]
    sys.modules[package_name] = package
    #module.__package__ = package_name

def find_existing_module_by_path(file_path):
    for name, module in sys.modules.items():
        if module.__file__ == os.path.abspath(file_path):
            return module

    return None

def check_file_is_importable(file_path, file_path_orig):
    if not os.path.exists(file_path):
        raise Error('File does not exist.', file_path=file_path_orig, file_path_resolved=file_path)

    if not os.path.isfile(file_path):
        raise Error('Object exists but is not a file.', file_path=file_path_orig, file_path_resolved=file_path)

    if not os.access(file_path, os.R_OK):
        raise Error('File exists but no read access.', file_path=file_path_orig, file_path_resolved=file_path)

def ultraimport(file_path, objects_to_import=None, globals=None, preprocessor=None, package=None, caller=None, caller_level=1, use_cache=True, lazy=False, recurse=False, inject=None, inject_override=None):
    if debug:
        print("ultraimport", file_path)

    file_path_orig = file_path

    # We are supposed to replace the string `__dir__` in file_path with the directory of the caller.
    # If the caller is not provided via parameter, we'll find it out ourselves.
    if not caller:
        import inspect
        caller = inspect.stack()[caller_level].filename

    if '__dir__' in file_path:
        file_path = file_path.replace('__dir__', os.path.dirname(caller))

    file_path = os.path.abspath(file_path)

    if lazy or (type(objects_to_import) == dict):
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
        raise ImportError(f"Circular import detected for '{file_path}' (resolved path: '{os.path.abspath(file_path)}')")

    with contextlib.ExitStack() as cleaner:
        cleaner.callback(import_ongoing_stack.pop, file_path, None)

        import_ongoing_stack[file_path] = True

        # TODO: Should we use resolved file_path for the cache?
        if use_cache and file_path in cache:
            module = cache[file_path]
        else:

            check_file_is_importable(file_path, file_path_orig)
            name = get_module_name(file_path)

            preprocessor_combined = preprocessor
            # If we want to recruse, we need to add our recurse preprocessor
            # to any other preprocessors from the user
            if recurse:
                if preprocessor:
                    def wrap_preprocessor(source):
                        source = preprocessor(source)
                        return transform_imports(source)
                    preprocessor_combined = wrap_preprocessor
                else:
                    preprocessor_combined = transform_imports

            loader = SourceFileLoader(name, file_path, preprocessor=preprocessor_combined, cache=use_cache)
            spec = importlib.util.spec_from_loader(name, loader)
            module = importlib.util.module_from_spec(spec)

            # Inject ultraimport module
            module.ultraimport = sys.modules[__name__]

            if inject:
                for k, v in inject.items():
                    setattr(module, k, v)

            package_name, package_path = get_package_name(file_path, package)
            #print('__package__', package_name)
            #print('__path__', package_path)
            if package_name:
                #import pkg_resources
                #pkg_resources.declare_namespace(package_name)
                #print('declared', sys.modules[package_name])
                package = CallableModule(package_name)
                package.__package__ = package_name
                package.__path__ = [ package_path ]
                sys.modules[package_name] = package
                module.__package__ = package_name
                #setattr(package, name, module)

            sys.modules[name] = module

            try:
                spec.loader.exec_module(module)
            except ImportError as e:
                #print(e.msg, e.name, e.path)
                if (e.msg == 'attempted relative import with no known parent package' or
                    e.msg == 'attempted relative import beyond top-level package'):
                    if recurse:
                        raise ImportError('This is an internal ultraimport error. Please report this bug and the circumstances!')
                    if package:
                        raise ImportError(f'ultraimport found an import ambiguity when importing {file_path}.\nYou need to either increase the level of package=int or, if that does not help, set recurse=True.')
                    else:
                        e.msg = f'ultraimport found an import ambiguity when importing {file_path}.\nYou need to either set the level of package=int or, if that does not help, set recurse=True.'
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
                    values.append(getattr(module, item))
                except AttributeError as e:
                    raise Error(str(e), file_path=file_path_orig, file_path_resolved=file_path) from None

            if globals:
                globals.update(zip(objects_to_import, values))

            if return_single:
                return values[0]

            return values
        elif globals:
            globals[module.__name__] = module

        if debug:
            print('module:', module)

        cache[file_path] = module

        return module

# Make ultraimport() directly callable after doing `import ultraimport`
class CallableModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return ultraimport(*args, caller_level=2, **kwargs)

sys.modules[__name__].__class__ = CallableModule
