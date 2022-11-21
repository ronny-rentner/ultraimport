<!-- markdownlint-disable -->

# `ultraimport` <kbd>module</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L0)</kbd>

## Module Variables

 - **reload_counter**
 - **cache**
 - **import_ongoing_stack**
 - **debug**

## `ultraimport` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L58)</kbd>

```python
ultraimport(
    file_path,
    objects_to_import=None,
    add_to_ns=None,
    preprocessor=None,
    package=None,
    caller=None,
    use_cache=True,
    lazy=False,
    recurse=False,
    inject=None,
    use_preprocessor_cache=True,
    cache_path_prefix=None
)
```

Import Python code files from the file system. This is the central main function of ultraimport.

**Parameters:**

 - **`file_path`** _(str)_:  Path to the module file that should be imported. It can have any file extension. Please be aware that you must provide the file extension. The path can be relative or absolute. You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`.

 - **`objects_to_import`** _(str | (Iterable[str] | Dict[str, object])_:  Can have several modes depending on the type of the parameter.
    - (str): Name of a single object to import from the module in `file_path`. The special value `'*'` selects all objects from that module.
    - (Iterable[str]): A list of names of objects to import.
    - (Dict[str, object]): The keys represent the names of the objects to import. The values define the expected types of those objects. A `TypeError` is thrown if the types don't match the expectation. If you set `lazy=True`, you must use a dict for `objects_to_import` and define the types.

 - **`add_to_ns`** _(Dict[str, object])_:  add the `objects_to_import` to the dict provided. Usually called with `add_to_ns=locals()` if you want the imported module to be added to the global namespace of the caller.

 - **`preprocessor`** _(callable)_:  Takes the source code as an argument and can return a modified version of the source code. Check out the [debug-transform example](/examples/working/debug-transform) on how to use the preprocessor.

 - **`package`** _(str | int)_:  Can have several modes depending on if you provide a string or an integer. If you provide a string, ultraimport will generate one or more namespace packages and use it as parent package of your imported module. If you set an integer, it means the number of path parts (directories) to extract from the `file_path` to calculate the namespace package. This can help with subsequent relative imports in your imported files. If `package` is set to the default `None`, the module will be imported without setting it parent `__package__`.

 - **`use_cache`** _(bool)_:  If set to `False`, allows re-importing of the same source file even if it was imported before. Otherwise a cached version of the imported module is returned.

 - **`lazy`** _(bool)_:  *Experimental* *wip* If set to `True` and if `objects_to_import` is set to `None`, it will lazy import the module. If set to True and `objects_to_import` is a dict, the values of the dict must be the type of the object to lazy import from the module. Currently only the type `callable` is supported.

 - **`recurse`** _(bool)_:  If set to `True`, a built-in preprocessor is activated to transparently rewrite all relative import statements (those with a dot like `from . import something`) to ultraimport() calls. Use this mode if you have no control over the source code of the impored modules.

 - **`cache_path_prefix`** _(str)_:  Directory for storing preprocessed files. If you use the preprocessor feature or if you use the option `recurse=True` (which in turn uses the preprocessor feature) you will have the option to store the resulting code after preprocessing. By default, they are stored in parallel to the original source code files, but this option allows to override to location. One common setting is `cache_path_prefix='__pycache__'` to store the processed files along with the bytecode files.
 - **`_Note_`**:  Even when you change this directory, this will be hidden from Python. Towards Python, the preprocessed files will always look like they are in the same directory as the original source code files, even if they are not.

**Returns:**
 Depending on the parameters *returns one of the following*:

 - **`object`**:  If `objects_to_import` is `None`, returns a single module object.

 - **`object`**:  If `objects_to_import` is a `str`, returns the single object with the specified name from the imported module.

 - **`dict`**:  If `objects_to_import` has the value `'*'`, returns a dict of all items from the imported module.

 - **`list`**:  If `objects_to_import` is a `List[str]`, return a list of imported objects from the imported module.

## `get_module_name` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L866)</kbd>

```python
get_module_name(file_path)
```

Return Python compatible module name from file_path. Replace dash and dot characters with underscore characters.

**Parameters:**

 - **`file_path`** _(str)_:  File path to a module or directory path to a package

**Returns:**

 - **`module_name`** _(str)_:  Extracted and escaped name of the module

## `get_package_name` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L887)</kbd>

```python
get_package_name(file_path, package)
```

Generate necessary package hierarchy according to the `package` parameter andcreate virtual namespace packages accordingly.

**Parameters:**

 - **`file_path`** _(str)_:  File path to a module or directory path to a package
 - **`package`** _(str)_:  Provide package name as a string. Can contain multiple parts separated by dots. The `__path__` of the package will be set to the parent directory of `file_path`.
 - **`package`** _(int)_:  Derive package name from the parent directory name(s) of `file_path` using <package> number of parent directories.

**Returns:**
 A tuple containing

 - **`package_name`** _(str)_:  Name of the package
 - **`package_path`** _(str)_:  Path to the package
 - **`package_module`** _(types.ModuleType)_:  Package module object

## `find_caller` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L922)</kbd>

```python
find_caller(return_frame=False)
```

Find out who is calling by looking at the stack and searching for the first external frame.

**Parameters:**

 - **`return_frame`** _(bool)_:  If True, also return the stack frame.

**Returns:**
 Depending on the parameters returns *one* of the following:

 - **`str`**:  A string with the caller name
 - **`str, frame`**:  A string with the caller name, the stack frame that was used to extract the caller name

## `create_ns_package` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L968)</kbd>

```python
create_ns_package(package_name, package_path, caller=None)
```

Create one or more dynamic namespace packages on the fly.

**Parameters:**

 - **`package_name`** _(str)_:  Name of the namespace package that should be created.

 - **`package_path`** _(str)_:  File system path of a directory that should be associated with the package. You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current working directory will be used for `__dir__`.

 - **`caller`** _(str)_:  File system path to the file of the calling module. If you use advanced debugging tools (or want to save some CPU cycles) you might want to set `caller=__file__`. Otherwise the caller is derrived from the frame stack.

## `find_existing_module_by_path` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L996)</kbd>

```python
find_existing_module_by_path(file_path)
```

## `check_file_is_importable` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L1003)</kbd>

```python
check_file_is_importable(file_path, file_path_orig)
```

## `reload` <kbd>function</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L1015)</kbd>

```python
reload(ns=None, add_to_ns=True)
```

Reload ultraimport module

--------------------------------

## `CodeInfo` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py)</kbd>

CodeInfo(source, file_path, line, offset)

--------------------------------

## `ErrorRendererMixin` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L318)</kbd>

Mixin for Exception classes with some helper functions, mainly for rendering data to console

### `ErrorRendererMixin.find_frame` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L356)</kbd>

```python
find_frame(frames, depth=1)
```

### `ErrorRendererMixin.render_header` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L342)</kbd>

```python
render_header(headline, message)
```

### `ErrorRendererMixin.render_suggestion` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L353)</kbd>

```python
render_suggestion(line1, line2)
```

### `ErrorRendererMixin.render_table` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L321)</kbd>

```python
render_table(data)
```

Render a table for error output on console output.

The tables are meant to always have to columns with labels in the firstcolumn and values in the second column.

--------------------------------

## `RewrittenImportError` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L367)</kbd>

### `RewrittenImportError.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L368)</kbd>

```python
__init__(message='', combine=None, code_info=None, object_to_import=None, *args)
```

### `RewrittenImportError.find_cause` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L409)</kbd>

```python
find_cause(tb=None, depth=0)
```

### `RewrittenImportError.find_frame` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L356)</kbd>

```python
find_frame(frames, depth=1)
```

### `RewrittenImportError.render_header` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L342)</kbd>

```python
render_header(headline, message)
```

### `RewrittenImportError.render_suggestion` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L353)</kbd>

```python
render_suggestion(line1, line2)
```

### `RewrittenImportError.render_table` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L321)</kbd>

```python
render_table(data)
```

Render a table for error output on console output.

The tables are meant to always have to columns with labels in the firstcolumn and values in the second column.

--------------------------------

## `CircularImportError` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L421)</kbd>

### `CircularImportError.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L422)</kbd>

```python
__init__(message=None, file_path=None, file_path_resolved=None, *args)
```

### `CircularImportError.find_frame` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L356)</kbd>

```python
find_frame(frames, depth=1)
```

### `CircularImportError.render_header` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L342)</kbd>

```python
render_header(headline, message)
```

### `CircularImportError.render_suggestion` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L353)</kbd>

```python
render_suggestion(line1, line2)
```

### `CircularImportError.render_table` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L321)</kbd>

```python
render_table(data)
```

Render a table for error output on console output.

The tables are meant to always have to columns with labels in the firstcolumn and values in the second column.

--------------------------------

## `ExecuteImportError` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L450)</kbd>

### `ExecuteImportError.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L451)</kbd>

```python
__init__(
    message=None,
    file_path=None,
    file_path_resolved=None,
    from_exception=None,
    depth=2,
    *args
)
```

### `ExecuteImportError.find_frame` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L356)</kbd>

```python
find_frame(frames, depth=1)
```

### `ExecuteImportError.render_header` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L342)</kbd>

```python
render_header(headline, message)
```

### `ExecuteImportError.render_suggestion` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L353)</kbd>

```python
render_suggestion(line1, line2)
```

### `ExecuteImportError.render_table` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L321)</kbd>

```python
render_table(data)
```

Render a table for error output on console output.

The tables are meant to always have to columns with labels in the firstcolumn and values in the second column.

--------------------------------

## `ResolveImportError` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L487)</kbd>

### `ResolveImportError.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L488)</kbd>

```python
__init__(
    message=None,
    file_path=None,
    file_path_resolved=None,
    from_exception=None,
    *args
)
```

### `ResolveImportError.find_frame` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L356)</kbd>

```python
find_frame(frames, depth=1)
```

### `ResolveImportError.render_header` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L342)</kbd>

```python
render_header(headline, message)
```

### `ResolveImportError.render_suggestion` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L353)</kbd>

```python
render_suggestion(line1, line2)
```

### `ResolveImportError.render_table` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L321)</kbd>

```python
render_table(data)
```

Render a table for error output on console output.

The tables are meant to always have to columns with labels in the firstcolumn and values in the second column.

--------------------------------

## `LazyCass` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L526)</kbd>

Lazily-loaded class that triggers module loading on access

--------------------------------

## `LazyCallable` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L532)</kbd>

Lazily-loaded callable that triggers module loading on access

### `LazyCallable.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L534)</kbd>

```python
__init__(importer, callable_name)
```

--------------------------------

## `LazyModule` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L545)</kbd>

Lazily-loaded module that triggers loading on attribute access

### `LazyModule.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L548)</kbd>

```python
__init__(name, file_path, importer)
```

--------------------------------

## `Loader` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L563)</kbd>

Loader factory that returns either SourceFileLoader or ExtensionFileLoader depending on file_path

--------------------------------

## `ExtensionFileLoader` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L573)</kbd>

--------------------------------

## `SourceFileLoader` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L576)</kbd>

Preprocessing Python source file loader

### `SourceFileLoader.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L579)</kbd>

```python
__init__(
    name,
    file_path,
    preprocessor=None,
    use_cache=True,
    cache_path_prefix=None
)
```

### `SourceFileLoader.check_preprocess` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L588)</kbd>

```python
check_preprocess(file_path)
```

### `SourceFileLoader.ensure_dir` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L617)</kbd>

```python
ensure_dir(path)
```

### `SourceFileLoader.get_data` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L658)</kbd>

```python
get_data(path, direct=False)
```

### `SourceFileLoader.get_filename` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L675)</kbd>

```python
get_filename(fullname)
```

### `SourceFileLoader.is_bytecode` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L641)</kbd>

```python
is_bytecode(file_path)
```

### `SourceFileLoader.path_stats` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L644)</kbd>

```python
path_stats(path)
```

### `SourceFileLoader.preprocess` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L622)</kbd>

```python
preprocess(file_path)
```

--------------------------------

## `RewriteImport` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L684)</kbd>

### `RewriteImport.__init__` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L686)</kbd>

```python
__init__(file_path=None, *args)
```

### `RewriteImport.gen_aliasses_tuple` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L807)</kbd>

```python
gen_aliasses_tuple(aliasses)
```

### `RewriteImport.gen_assign` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L729)</kbd>

```python
gen_assign(targets, value)
```

### `RewriteImport.gen_call` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L740)</kbd>

```python
gen_call(name, args=[], keywords=[])
```

### `RewriteImport.gen_code_info` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L762)</kbd>

```python
gen_code_info(source, file_path, line, offset)
```

### `RewriteImport.gen_import` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L794)</kbd>

```python
gen_import(alias, module_path, object_name=None)
```

### `RewriteImport.gen_import_call` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L743)</kbd>

```python
gen_import_call(file_path, import_elts=None)
```

### `RewriteImport.gen_keyword` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L735)</kbd>

```python
gen_keyword(name, value)
```

### `RewriteImport.gen_objects_tuple` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L810)</kbd>

```python
gen_objects_tuple(object_names)
```

### `RewriteImport.gen_raise` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L772)</kbd>

```python
gen_raise(alias, code_info, combine, object_to_import)
```

### `RewriteImport.gen_try` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L713)</kbd>

```python
gen_try(
    try_body,
    except_body=<ast.Pass object at 0x7ffaf6ac8820>,
    except_alias='e',
    except_error='ultraimport.ResolveImportError'
)
```

### `RewriteImport.transform_imports` <kbd>classmethod</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L690)</kbd>

```python
transform_imports(source, file_path=None, use_cache=True)
```

### `RewriteImport.visit_ImportFrom` <kbd>method</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L815)</kbd>

```python
visit_ImportFrom(node)
```

Rewrite all `import .. from` statements

--------------------------------

## `CallableModule` <kbd>class</kbd> <kbd>[:link: source](https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L1024)</kbd>

Makes ultraimport directly callable after doing `import ultraimport`

