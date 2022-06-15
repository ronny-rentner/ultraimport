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
import os, sys, contextlib, types
import ast

cache = {}
import_ongoing_stack = {}

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

class UltraSourceFileLoader(importlib.machinery.SourceFileLoader):
    """ Preprocessing Python source file loader """

    def __init__(self, name, file_path, preprocessor = None):
        super().__init__(name, file_path)
        self.preprocessor = preprocessor
        if self.preprocessor:
            self.check_preprocess(file_path)

    def check_preprocess(self, file_path):
        file_name, file_extension = os.path.splitext(file_path)
        self.preprocess_file_path = f"{file_name}__preprocessed__{file_extension}"

        if os.path.exists(self.preprocess_file_path):
            preprocessed = os.stat(self.preprocess_file_path)
            original = os.stat(file_path)
            if original.st_mtime > preprocessed.st_mtime:
                self.preprocess(file_path)
        else:
            self.preprocess(file_path)

    def preprocess(self, file_path):
        #print('preprocess', file_path)
        code = self.get_data(file_path)
        code = self.preprocessor(code)
        # Write processed code back for caching
        with open(self.preprocess_file_path, 'wb') as f:
            f.write(f"# NOTE: This file was automatically generated from:\n# {file_path}\n# DO NOT CHANGE DIRECTLY!\n".encode())
            f.write(code)
        #os.utime(self.preprocess_file_path, (original['mtime'], original['mtime']))

    def is_bytecode(self, file_path):
        return file_path[file_path.rindex("."):] in importlib.machinery.BYTECODE_SUFFIXES

    #def path_stats(self, path):
        # Invalidate bytecode cache
        #raise OSError

    def get_filename(self, fullname):
        #print('get_filename', fullname, self.path)
        if self.preprocessor:
            return self.preprocess_file_path
        return self.path

class RewriteImport(ast.NodeTransformer):

    def visit_ImportFrom(self, node):
        node = self.generic_visit(node)

        if not node.module:
            imports = []
            module_pathes = [ f"__dir__/{(node.level - 1) * '../'}{n.name}.py" for n in node.names ]
            aliases_to_import = [ n.asname if n.asname else n.name for n in node.names ]

            for alias, module_path in zip(aliases_to_import, module_pathes):
                un = ast.Assign(targets=[ast.Name(id=alias, ctx=ast.Store())], value=ast.Call(func=ast.Name(id='ultraimport', ctx=ast.Load()), args=[ast.Constant(value=module_path)], keywords=[ast.keyword(arg='recurse', value=ast.Constant(value=True))]))
                imports.append(un)
                ast.copy_location(un, node)
            return imports

        objects_to_import = tuple( n.name for n in node.names )
        import_elts = ast.Tuple(elts=[ ast.Constant(value=name) for name in objects_to_import ], ctx=ast.Load())
        aliases_to_import = tuple( n.asname if n.asname else n.name for n in node.names )
        aliases_elts = ast.Tuple(elts=[ ast.Name(id=alias, ctx=ast.Store()) for alias in aliases_to_import ], ctx=ast.Store())

        module_path = '__dir__/' + ((node.level - 1) * '../') + node.module + '.py'

        un = ast.Assign(targets=[aliases_elts], value=ast.Call(func=ast.Name(id='ultraimport', ctx=ast.Load()), args=[ast.Constant(value=module_path), import_elts], keywords=[ast.keyword(arg='recurse', value=ast.Constant(value=True))]))

        return ast.copy_location(un, node)

def transform_imports(source):
    tree = ast.parse(source)
    #print('---------')
    #print(ast.dump(tree))
    #print('---------')

    tree = ast.fix_missing_locations(RewriteImport().visit(tree))
    unparsed = ast.unparse(tree)

    #print('---------')
    #print(unparsed)
    #print('---------')

    return unparsed.encode()

def get_module_name(file_path):
    """ Calculate Python compatible module name from file_path """
    base_name = os.path.basename(file_path)
    name, file_extension = os.path.splitext(base_name)
    return name.replace('-', '_').replace('.', '_')

def get_package_name(file_path, package):
    if type(package) == str:
        return package
    elif type(package) == int:
        return '.'.join(os.path.dirname(os.path.abspath(file_path)).split(os.sep)[-package:])
    return None

def ultraimport(file_path, objects_to_import = None, globals=None, preprocessor=None, package=None, caller=None, caller_level=1, use_cache=True, lazy=False, recurse=False):

    #print("ultra", file_path)

    if '__dir__' in file_path:
        if not caller:
            import inspect
            caller = inspect.stack()[caller_level].filename
        file_path = file_path.replace('__dir__', os.path.dirname(caller))

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
        raise ImportError(f"Circular import detected for '{file_path}' (resolved path: '{os.path.abspath(file_path)}')")

    with contextlib.ExitStack() as cleaner:
        cleaner.callback(import_ongoing_stack.pop, file_path, None)

        import_ongoing_stack[file_path] = True

        if use_cache and file_path in cache:
            module = cache[file_path]
        else:
            if not os.path.exists(file_path):
                raise ImportError(f"'{file_path}' does not exist (resolved path: '{os.path.abspath(file_path)}')")

            name = get_module_name(file_path)

            _pre = preprocessor
            if recurse:
                def _(source):
                    source = preprocessor(source)
                    return transform_imports(source)
                _pre = _
            loader = UltraSourceFileLoader(name, file_path, _pre)
            spec = importlib.util.spec_from_loader(name, loader)
            module = importlib.util.module_from_spec(spec)

            # Inject ultraimport() function into module
            module.ultraimport = ultraimport

            package_name = get_package_name(file_path, package)
            if package_name:
                #print('package_name', package_name)
                module.__package__ = package_name

            sys.modules[name] = module
            cache[file_path] = module

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
                        raise ImportError(f'ultraimport found an import ambiguity when importing {file_path}.\nYou need to either set the level of package=int or, if that does not help, set recurse=True.')
                raise e


        if objects_to_import:
            return_single = False
            if objects_to_import == '*':
                objects_to_import = [ item for item in dir(module) if not item.startswith('__') ]
            elif type(objects_to_import) == str:
                objects_to_import = [ objects_to_import ]
                return_single = True

            values = [ getattr(module, item) for item in objects_to_import ]

            if globals:
                globals.update(zip(objects_to_import, values))

            if return_single:
                return values[0]

            return values
        elif globals:
            globals[module.__name__] = module


        return module

# Make ultraimport() directly callable after doing `import ultraimport`
class CallableModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return ultraimport(*args, caller_level=2, **kwargs)

sys.modules[__name__].__class__ = CallableModule

