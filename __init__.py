#
# ultraimport
#
# Stable, File-based Python Imports
#
# Copyright [2022] [Ronny Rentner] [ultraimport@ronny-rentner.de]
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

import importlib, os, pathlib, sys

cache = {}

#@profile
def ultraimport(file_path, objects_to_import = None, globals=None, caller=None, use_cache=True):

    if use_cache and file_path in cache:
        module = cache[file_path]
    else:
        if '__dir__' in file_path:
            if not caller:
                import inspect
                caller = inspect.stack()[1].filename
            file_path = file_path.replace('__dir__', os.path.dirname(caller))

        def fix_name(file_path):
            name = file_path[:-3] if file_path.endswith('.py') else file_path
            return name.replace('-', '_').replace('.', '_')

        if not os.path.exists(file_path):
            raise ImportError(f"'{file_path}' does not exist (resolved path: '{os.path.abspath(file_path)}')")

        name = fix_name(file_path)
        #file_path = os.path.abspath(file_path)

        loader = importlib.machinery.SourceFileLoader(name, file_path)
        spec = importlib.util.spec_from_loader(name, loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        #spec = importlib.util.spec_from_file_location(name, os.path.abspath(file_path))
        #module = importlib.util.module_from_spec(spec)

        # Optional; only necessary if you want to be able to import the module
        # by name later.
        sys.modules[name] = module

        dir_name = os.path.dirname(file_path)
        if dir_name not in sys.path:
            sys.path.append(dir_name)

        cache[file_path] = module

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

        return objects_to_import

    return module

# Hack to make ultraimport() directly callable after doing `import ultraimport`
sys.modules[__name__] = ultraimport
