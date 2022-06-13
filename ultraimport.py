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

cache = {}
import_ongoing_stack = {}

class LazyCallable():
    """ Class for lazily-loaded callables that triggers module loading on access """
    def __init__(self, importer, callable_name):
        self._importer = importer
        self._callable_name = callable_name

    def __call__(self, *args, **kwargs):
        if not hasattr(self, '_callable'):
            imported_module = self._importer()
            self._callable = getattr(imported_module, self._callable_name)

        return self._callable(*args, **kwargs)

class LazyModule(types.ModuleType):

    def __init__(self, name, file_path, importer):
        super().__init__(name)
        self._importer = importer
        self.__file__ = file_path

    def __getattr__(self, key):
        if key == '_module':
            self._module = self._importer()
            return self._module
        return self._module.__getattribute__(key)

    #def __reduce__(self):
    #    return (self.__class__, (self._name, self.__file__, self._import_structure))

class UltraSourceFileLoader(importlib.machinery.SourceFileLoader):

    def __init__(self, name, file_path, preprocessor = None):
        super().__init__(name, file_path)
        self.preprocessor = preprocessor
        if self.preprocessor:
            self.check_preprocess(file_path)

    def check_preprocess(self, file_path):
        #print('check_preprocess', file_path)

        self.preprocess_file_path = file_path[:-3] + '__preprocessed__.py'

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
            f.write(code)
        #os.utime(self.preprocess_file_path, (original['mtime'], original['mtime']))

    def is_bytecode(self, file_path):
        return file_path[file_path.rindex("."):] in importlib.machinery.BYTECODE_SUFFIXES

    #def path_stats(self, path):
        #raise OSError

    #def get_data(self, path):
    #    print('get_data', path, self.path)
    #    return super().get_data(path)

    def get_filename(self, fullname):
        #print('get_filename', fullname, self.path)
        if self.preprocessor:
            return self.path[:-3] + '__preprocessed__.py'
        return self.path

def get_name(file_path):
    base_name = os.path.basename(file_path)
    name = base_name[:-3] if base_name.endswith('.py') else base_name
    return name.replace('-', '_').replace('.', '_')


def ultraimport(file_path, objects_to_import = None, globals=None, preprocessor=None, caller=None, caller_level=1, use_cache=True, lazy=False):

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
            name = get_name(file_path)
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

            #print("lazy: ", objects_to_import)

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

            name = get_name(file_path)
            #file_path = os.path.abspath(file_path)

            loader = UltraSourceFileLoader(name, file_path, preprocessor)
            spec = importlib.util.spec_from_loader(name, loader)
            module = importlib.util.module_from_spec(spec)

            #spec = importlib.util.spec_from_file_location(name, os.path.abspath(file_path))
            #module = importlib.util.module_from_spec(spec)

            sys.modules[name] = module

            cache[file_path] = module

            #dir_name = os.path.dirname(file_path)
            #if dir_name not in sys.path:
            #    sys.path.append(dir_name)

            spec.loader.exec_module(module)


        if objects_to_import:
            if objects_to_import == '*':
                objects_to_import = [ item for item in dir(module) if not item.startswith('__') ]
            elif type(objects_to_import) == str:
                objects_to_import = [ objects_to_import ]

            objects_to_import = { item: getattr(module, item) for item in objects_to_import }

            if globals:
                globals.update(objects_to_import)

            if len(objects_to_import) == 1:
                return list(objects_to_import.values())[0]

            return list(objects_to_import.values())

        return module

# Hack to make ultraimport() directly callable after doing `import ultraimport`
class CallableModule(types.ModuleType):
    def __call__(self, *args, **kwargs):
        return ultraimport(*args, caller_level=2, **kwargs)

sys.modules[__name__].__class__ = CallableModule

