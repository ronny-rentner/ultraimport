<!-- markdownlint-disable -->

# API Overview

## Modules

- [`ultraimport`](./ultraimport.md#module-ultraimport)

## Classes

- [`ultraimport.CallableModule`](./ultraimport.md#class-callablemodule): Makes ultraimport directly callable after doing `import ultraimport` 
- [`ultraimport.CircularImportError`](./ultraimport.md#class-circularimporterror)
- [`ultraimport.CodeInfo`](./ultraimport.md#class-codeinfo): CodeInfo(source, file_path, line, offset)
- [`ultraimport.ErrorRendererMixin`](./ultraimport.md#class-errorrenderermixin): Mixin for Exception classes with some helper functions, mainly for rendering data to console 
- [`ultraimport.ExecuteImportError`](./ultraimport.md#class-executeimporterror)
- [`ultraimport.ExtensionFileLoader`](./ultraimport.md#class-extensionfileloader)
- [`ultraimport.LazyCallable`](./ultraimport.md#class-lazycallable): Lazily-loaded callable that triggers module loading on access 
- [`ultraimport.LazyCass`](./ultraimport.md#class-lazycass): Lazily-loaded class that triggers module loading on access 
- [`ultraimport.LazyModule`](./ultraimport.md#class-lazymodule): Lazily-loaded module that triggers loading on attribute access 
- [`ultraimport.Loader`](./ultraimport.md#class-loader): Loader factory that returns either SourceFileLoader or ExtensionFileLoader depending on file_path 
- [`ultraimport.ResolveImportError`](./ultraimport.md#class-resolveimporterror)
- [`ultraimport.RewriteImport`](./ultraimport.md#class-rewriteimport)
- [`ultraimport.RewrittenImportError`](./ultraimport.md#class-rewrittenimporterror)
- [`ultraimport.SourceFileLoader`](./ultraimport.md#class-sourcefileloader): Preprocessing Python source file loader 

## Functions

- [`ultraimport.check_file_is_importable`](./ultraimport.md#function-check_file_is_importable)
- [`ultraimport.create_ns_package`](./ultraimport.md#function-create_ns_package): Create one or more dynamic namespace packages on the fly.
- [`ultraimport.find_caller`](./ultraimport.md#function-find_caller): Find out who is calling by looking at the stack and searching for the first external frame.
- [`ultraimport.find_existing_module_by_path`](./ultraimport.md#function-find_existing_module_by_path)
- [`ultraimport.get_module_name`](./ultraimport.md#function-get_module_name): Return Python compatible module name from file_path. Replace dash and dot characters with underscore characters.
- [`ultraimport.get_package_name`](./ultraimport.md#function-get_package_name): Generate necessary package hierarchy according to the `package` parameter and
- [`ultraimport.reload`](./ultraimport.md#function-reload): Reload ultraimport module 
- [`ultraimport.ultraimport`](./ultraimport.md#function-ultraimport): Import Python code files from the file system. This is the central main function of ultraimport.
