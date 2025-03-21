# Ultraimport Examples

This directory contains examples demonstrating various features and use cases for ultraimport.

## Core Examples

- **[quickstart](./quickstart/)** - Basic usage patterns for getting started
- **[myprogram](./myprogram/)** - Simple program with relative imports
- **[mypackage](./mypackage/)** - More complex example with nested packages

## Advanced Features

- **[dependency-injection](./dependency-injection/)** - Inject dependencies into imported modules
- **[recurse](./recurse/)** - Automatically rewrite relative imports
- **[debug-transform](./debug-transform/)** - Use preprocessors to transform code before import
- **[preprocess-packed](./preprocess-packed/)** - Dynamic JSX-style preprocessing without manual steps
- **[dynamic-namespace](./dynamic-namespace/)** - Create virtual namespace packages
- **[impossible-filename](./impossible-filename/)** - Import from paths that would normally be impossible

## Advanced Use Cases

- **[stackoverflow-74632397](./stackoverflow-74632397/)** - Work with auto-generated code without modifying it
  
  This example demonstrates one of ultraimport's most powerful capabilities: making imports work correctly in code that would otherwise be difficult or impossible to modify. It shows how to work with auto-generated files, legacy code, or third-party libraries by providing the correct import context dynamically.

- **[cursed-for](./cursed-for/)** - Extend Python syntax with custom constructs
- **[typed-imports](./typed-imports/)** - Enforce type checking during imports

## Stack Overflow Solutions

- **[stackoverflow-11536764](./stackoverflow-11536764/)** - Solution to a package import question
- **[stackoverflow-63145047](./stackoverflow-63145047/)** - Solution to a nested package import question

## Experimental Features

- **[missing-import-injection](./recurse/inject_missing.py)** - Fix missing imports with dependency injection