# ultraimport: Better Error Messages
When an import fails with ultraimport, either a direct `ultraimport()` call or a rewritten relative import using `recurse=True`, ultraimport tries to present a useful error message taht can actually help you solve the problem.

## Example 1:
Let's try to import the `mypackage.mymodule` module from our [recurse example](/working/recurse), but we'll keep our current working directory (which is this repo checked out).
```pycon
>>> ultraimport('__dir__/working/recurse/mypackage/mymodule')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 738, in __call__
    return ultraimport(*args, caller_level=2, **kwargs)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 638, in ultraimport
    check_file_is_importable(file_path, file_path_orig)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 565, in check_file_is_importable
    raise ResolveImportError('File does not exist.', file_path=file_path_orig, file_path_resolved=file_path)
ultraimport.ResolveImportError: 

┌──────────────────────┐
│ Resolve Import Error │
└──────────────────────┘

An import file could not be found or not be read.

   Import file_path │ __dir__/working/recurse/mypackage/mymodule
 Resolved file_path │ /home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule
    Possible reason │ File does not exist.

 ╲ Did you mean to import '/home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule.py'?
 ╱ You need to add the file extension '.py' to the file_path.

```

You'll get a hint on what was the resolved path and what could be the cause of the error. In this case it's a missing file extension because `ultraimport()` imports files.

## Example 2:
Let's correct the error from our first example and add the .py file extension:
```pycon
>>> ultraimport('__dir__/working/recurse/mypackage/mymodule.py')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 705, in __call__
    return ultraimport(*args, caller_level=2, **kwargs)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 659, in ultraimport
    raise ExecuteImportError('Unhandled, relative import statement found.', file_path=file_path_orig, file_path_resolved=file_path, from_exception=e).with_traceback(e.__traceback__) from None
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 648, in ultraimport
    spec.loader.exec_module(module)
  File "<frozen importlib._bootstrap_external>", line 790, in exec_module
  File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
  File "/home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule.py", line 12, in <module>
    from .logger import log, other_logger as log2
ultraimport.ExecuteImportError: 

┌──────────────────────┐
│ Execute Import Error │
└──────────────────────┘

An import file could be found and read, but an error happened while executing it.

     Source file │ /home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule.py, line 12
      Happend in │ <module>
     Source code │ from .logger import log, other_logger as log2
 Possible reason │ A subsequent, relative import statement was found, but not handled.
 Original errror │ "attempted relative import with no known parent package"

 ╲ To handle the relative import from above, use the ultraimport() parameter `recurse=True`.
 ╱ This will activate automatic rewriting of subsequent, relative imports.

```

Ok, now it found the file `mymodule.py` but in there is another relative import statement for the `logger` module that has failed.

## Example 3:
We actually have two different options now, but let's follow the suggestion from above and use `recurse=True`.
```pycon
>>> ultraimport('__dir__/working/recurse/mypackage/mymodule.py', recurse=True)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 723, in __call__
    return ultraimport(*args, caller_level=2, **kwargs)
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 680, in ultraimport
    raise e
  File "/home/ronny/Projects/py/ultraimport/ultraimport.py", line 662, in ultraimport
    spec.loader.exec_module(module)
  File "<frozen importlib._bootstrap_external>", line 790, in exec_module
  File "<frozen importlib._bootstrap>", line 228, in _call_with_frames_removed
  File "/home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule__preprocessed__.py", line 23, in <module>
    raise ultraimport.RewrittenImportError(code_info=('from . import log, other_logger as log2', '/home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule.py', 6, 0), object_to_import='other_logger', combine=[e, e2, e3]) from None
ultraimport.RewrittenImportError: 

┌────────────────────────┐
│ Rewritten Import Error │
└────────────────────────┘

A relative import statement was transparently rewritten and failed.

     Original source file │ '/home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule.py', line 6:0
     Original source code │ from . import log, other_logger as log2
 Preprocessed source file │ '/home/ronny/Projects/py/ultraimport/working/recurse/mypackage/mymodule__preprocessed__.py', line 21
            Error details │ Could not find resource 'other_logger' in any of the following files:
                          │ - /home/ronny/Projects/py/ultraimport/working/recurse/mypackage/__init__.py
                          │   (Possible reason: module '__init__' has no attribute 'other_logger')
                          │ - /home/ronny/Projects/py/ultraimport/working/recurse/mypackage/other_logger/__init__.py
                          │   (Possible reason: File does not exist.)
                          │ - /home/ronny/Projects/py/ultraimport/working/recurse/mypackage/other_logger.py
                          │   (Possible reason: File does not exist.)

 ╲ Check if the required package or module really exists in your file system.
 ╱ If you know the path but cannot change the import statement, use dependency injection to inject the resource.
```

In the error details, we see that the resource 'other_logger' cannot be found and we also see a list of files that Python has searched. We could now check where this other_logger actually is.


