<!-- markdownlint-disable -->

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L0"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

# <kbd>module</kbd> `ultraimport`




**Global Variables**
---------------
- **reload_counter**
- **cache**
- **import_ongoing_stack**
- **debug**

---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L600"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_module_name`

```python
get_module_name(file_path)
```

Return Python compatible module name from file_path. Replace dash and dot characters with underscore characters. 



**Parameters:**
 
 - <b>`file_path`</b> (str):  File path to a module or directory path to a package 



**Returns:**
 
 - <b>`module_name`</b> (str):  Extracted and escaped name of the module 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L621"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `get_package_name`

```python
get_package_name(file_path, package)
```

Generate necessary package hierarchy according to the `package` parameter and create virtual namespace packages accordingly. 



**Parameters:**
 
 - <b>`file_path`</b> (str):  File path to a module or directory path to a package 
 - <b>`package`</b> (str):  Provide package name as a string. Can contain multiple parts separated by dots.  The `__path__` of the package will be set to the parent directory of `file_path`. 
 - <b>`package`</b> (int):  Derive package name from the parent directory name(s) of `file_path` using <package> number  of parent directories. 



**Returns:**
 A tuple containing: 
 - <b>`package_name`</b> (str):  Name of the package 
 - <b>`package_path`</b> (str):  Path to the package 
 - <b>`package_module`</b> (module):  Package module object 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L655"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `find_caller`

```python
find_caller(return_frame=False)
```

Find out who is calling by looking at the stack and searching for the first external frame. 



**Parameters:**
 
 - <b>`return_frame`</b> (bool):  If True, also return the stack frame. 



**Returns:**
 Depending on the parameters returns *one* of the following: 
 - <b>`str`</b>:  A string with the caller name 
 - <b>`str, frame`</b>:  A string with the caller name, the stack frame that was used to extract the caller name 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L700"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `create_ns_package`

```python
create_ns_package(package_name, package_path, caller=None)
```

Create one or more dynamic namespace packages on the fly. 



**Parameters:**
 
 - <b>`package_name`</b> (str):  Name of the namespace package that should be created. 


 - <b>`package_path`</b> (str):  File system path of a directory that should be associated with the package.  You can use the special string `__dir__` to refer to the directory of the caller. If run from a Python  REPL, the current working directory will be used for `__dir__`. 


 - <b>`caller`</b> (str):  File system path to the file of the calling module. If you use advanced debugging tools  (or want to save some CPU cycles) you might want to set `caller=__file__`. Otherwise the caller  is derrived from the frame stack. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L728"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `find_existing_module_by_path`

```python
find_existing_module_by_path(file_path)
```






---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L735"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `check_file_is_importable`

```python
check_file_is_importable(file_path, file_path_orig)
```






---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L747"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `ultraimport`

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

Import Python code files from the file system. 



**Parameters:**
 
 - <b>`file_path`</b> (str):  Path to the module file that should be imported. It can have any file extension. Please be  aware that you must provide the file extension. The path can be relative or absolute. You can use the  special string `__dir__` to refer to the directory of the caller. If run from a Python REPL, the current  working directory will be used for `__dir__`. If you use advanced debugging tools (or want to save some  CPU cycles) you might want to set `caller=__file__`. 


 - <b>`objects_to_import`</b>:  Can have several modes depending on the type of the parameter. 
    - (str): Provide the name of a single object to import from the module in `file_path` or use the value `'*'`  to import all objects from that module. 
    - (Iterable[str]): Provide names of objects to import. 
    - (Dict[str, object]): The keys represent the names of the objects to import. The values define  the expected types of the objects to import. A `TypeError` is thrown if the types don't match the  expectation.  If you set `lazy=True`, you must use a dict for `objects_to_import` and define the types. 


 - <b>`add_to_ns`</b> (Dict[str, object]):  add the `objects_to_import` to the dict provided. Usually called with  `add_to_ns=locals()` if you want the imported module to be added to the global namespace of the caller. 


 - <b>`preprocessor`</b> (callable):  Takes the source code as an argument and can return a modified version of the source code. Check out the [debug-transform example](/examples/working/debug-transform) on how to use the preprocessor. 


 - <b>`package`</b> (str | int):  Can have several modes depending on if you provide a string or an integer. If you provide  a string, ultraimport will generate one or more namespace packages and use it as parent package of your  imported module. If you set an integer, it means the number of path parts (directories) to extract from the  `file_path` to calculate the namespace package. This can help with subsequent relative imports in your  imported files. If `package` is set to the default `None`, the module will be imported without setting it  parent `__package__`. 


 - <b>`use_cache`</b> (bool):  If set to `False`, allows re-importing of the same source file even if it was imported before.  Otherwise a cached version of the imported module is returned. 


 - <b>`lazy`</b> (bool):  *Experimental* *wip* If set to `True` and if `objects_to_import` is set to `None`, it will lazy  import the module. If set to True and `objects_to_import` is a dict, the values of the dict must be the  type of the object to lazy import from the module. Currently only the type `callable` is supported. 


 - <b>`recurse`</b> (bool):  If set to `True`, a built-in preprocessor is activated to transparently rewrite all relative  import statements (those with a dot like `from . import something`) to ultraimport() calls. Use this mode  if you have no control over the source code of the impored modules. 


 - <b>`cache_path_prefix`</b> (str):  Directory for storing preprocessed files. If you use the preprocessor feature or if  you use the option `recurse=True` (which in turn uses the preprocessor feature) you will have the option to  store the resulting code after preprocessing. By default, they are stored in parallel to the original  source code files, but this option allows to override to location. One common setting is  `cache_path_prefix='__pycache__'` to store the processed files along with the bytecode files. 
 - <b>`_Note_`</b>:  Even when you change this directory, this will be hidden from Python. Towards Python, the preprocessed files will always look like they are in the same directory as the original source code files, even if they are not. 



**Returns:**
 Depending on the parameters *returns one of the following*: 


 - <b>`object`</b>:  If `objects_to_import` is `None`, returns a single module object. 


 - <b>`object`</b>:  If `objects_to_import` is a `str`, returns the single object with the specified name from the imported module. 


 - <b>`dict`</b>:  If `objects_to_import` has the value `'*'`, returns a dict of all items from the imported module. 


 - <b>`list`</b>:  If `objects_to_import` is a `List[str]`, return a list of imported objects from the imported module. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L1000"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>function</kbd> `reload`

```python
reload(ns=None, add_to_ns=True)
```

Reload ultraimport module  


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CodeInfo`
CodeInfo(source, file_path, line, offset) 





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L63"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ErrorRendererMixin`
Mixin for Exception classes with some helper functions, mainly for rendering data to console  




---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_frame`

```python
find_frame(frames, depth=1)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_header`

```python
render_header(headline, message)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_suggestion`

```python
render_suggestion(line1, line2)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_table`

```python
render_table(data)
```

Render a table for error output on console output. 

The tables are meant to always have to columns with labels in the first column and values in the second column. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L112"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RewrittenImportError`




<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L113"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message='', combine=None, code_info=None, object_to_import=None, *args)
```








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L154"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_cause`

```python
find_cause(tb=None, depth=0)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_frame`

```python
find_frame(frames, depth=1)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_header`

```python
render_header(headline, message)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_suggestion`

```python
render_suggestion(line1, line2)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_table`

```python
render_table(data)
```

Render a table for error output on console output. 

The tables are meant to always have to columns with labels in the first column and values in the second column. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L166"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CircularImportError`




<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L167"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(message=None, file_path=None, file_path_resolved=None, *args)
```








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_frame`

```python
find_frame(frames, depth=1)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_header`

```python
render_header(headline, message)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_suggestion`

```python
render_suggestion(line1, line2)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_table`

```python
render_table(data)
```

Render a table for error output on console output. 

The tables are meant to always have to columns with labels in the first column and values in the second column. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L195"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExecuteImportError`




<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L196"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

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








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_frame`

```python
find_frame(frames, depth=1)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_header`

```python
render_header(headline, message)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_suggestion`

```python
render_suggestion(line1, line2)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_table`

```python
render_table(data)
```

Render a table for error output on console output. 

The tables are meant to always have to columns with labels in the first column and values in the second column. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L232"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ResolveImportError`




<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L233"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    message=None,
    file_path=None,
    file_path_resolved=None,
    from_exception=None,
    *args
)
```








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L101"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `find_frame`

```python
find_frame(frames, depth=1)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L87"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_header`

```python
render_header(headline, message)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L98"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_suggestion`

```python
render_suggestion(line1, line2)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L66"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `render_table`

```python
render_table(data)
```

Render a table for error output on console output. 

The tables are meant to always have to columns with labels in the first column and values in the second column. 


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L271"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LazyCass`
Lazily-loaded class that triggers module loading on access  





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L277"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LazyCallable`
Lazily-loaded callable that triggers module loading on access  

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L279"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(importer, callable_name)
```









---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L290"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `LazyModule`
Lazily-loaded module that triggers loading on attribute access  

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L293"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(name, file_path, importer)
```









---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L304"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `Loader`
Loader factory that returns either SourceFileLoader or ExtensionFileLoader depending on file_path  





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L314"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `ExtensionFileLoader`








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L317"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `SourceFileLoader`
Preprocessing Python source file loader  

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L320"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(
    name,
    file_path,
    preprocessor=None,
    use_cache=True,
    cache_path_prefix=None
)
```








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L329"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `check_preprocess`

```python
check_preprocess(file_path)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L358"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `ensure_dir`

```python
ensure_dir(path)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L399"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_data`

```python
get_data(path, direct=False)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L416"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `get_filename`

```python
get_filename(fullname)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L382"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `is_bytecode`

```python
is_bytecode(file_path)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L385"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `path_stats`

```python
path_stats(path)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L363"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `preprocess`

```python
preprocess(file_path)
```






---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L421"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `RewriteImport`




<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L423"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `__init__`

```python
__init__(file_path=None, *args)
```








---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L544"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_aliasses_tuple`

```python
gen_aliasses_tuple(aliasses)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L466"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_assign`

```python
gen_assign(targets, value)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L477"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_call`

```python
gen_call(name, args=[], keywords=[])
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L499"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_code_info`

```python
gen_code_info(source, file_path, line, offset)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L531"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_import`

```python
gen_import(alias, module_path, object_name=None)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L480"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_import_call`

```python
gen_import_call(file_path, import_elts=None)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L472"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_keyword`

```python
gen_keyword(name, value)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L547"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_objects_tuple`

```python
gen_objects_tuple(object_names)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L509"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_raise`

```python
gen_raise(alias, code_info, combine, object_to_import)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L450"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `gen_try`

```python
gen_try(
    try_body,
    except_body=<ast.Pass object at 0x7f1073178820>,
    except_alias='e',
    except_error='ultraimport.ResolveImportError'
)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L427"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>classmethod</kbd> `transform_imports`

```python
transform_imports(source, file_path=None, use_cache=True)
```





---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L552"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

### <kbd>method</kbd> `visit_ImportFrom`

```python
visit_ImportFrom(node)
```

Rewrite all `import .. from` statements  


---

<a href="https://github.com/ronny-rentner/ultraimport/blob/main/ultraimport.py#L1009"><img align="right" style="float:right;" src="https://img.shields.io/badge/-source-cccccc?style=flat-square"></a>

## <kbd>class</kbd> `CallableModule`
Makes ultraimport directly callable after doing `import ultraimport`  





