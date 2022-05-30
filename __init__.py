import importlib, os, pathlib, sys

def ultraimport(file_path, map_to_globals = None, globals=None):

    if '__dir__' in file_path:
        import inspect
        caller = inspect.stack()[1].filename
        file_path = file_path.replace('__dir__', str(pathlib.Path(caller).parent))

    def fix_name(file_path):
        name = file_path.name.removesuffix('.py')
        return str(name).replace('-', '_').replace('.', '_')

    if type(file_path) == str:
        file_path = pathlib.Path(file_path)

    if not file_path.exists():
        raise ImportError(f"'{file_path}' does not exist (resolved path: '{file_path.resolve()}')")

    name = fix_name(file_path)
    loader = importlib.machinery.SourceFileLoader(name, str(file_path.resolve()))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)

    dir_name = os.path.dirname(file_path)
    if dir_name not in sys.path:
        sys.path.append(dir_name)

    if map_to_globals:
        if map_to_globals == '*':
            map_to_globals = [ item for item in dir(module) if not item.startswith('__') ]
        elif type(map_to_globals) == str:
            map_to_globals = [ map_to_globals ]

        map_to_globals = { item: getattr(module, item) for item in map_to_globals }

        if globals:
            globals.update(map_to_globals)

        if len(map_to_globals) == 1:
            return list(map_to_globals.values())[0]

        return map_to_globals

    return module

# Hack to make ultraimport() directly callable after doing `import ultraimport`
sys.modules[__name__] = ultraimport
