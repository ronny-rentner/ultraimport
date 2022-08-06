# ultraimport: Advanced Usage

See [ultraimport Github Page](https://github.com/ronny-rentner/ultraimport) for an overview.

## Import impossible filename and directory

With ultraimport, you can import from any file or directory, even if it contains spaces or dashes or if the file name contains any other file extension.

See [example](/examples/working/impossible-filename)

run.py:
```python
import ultraimport

ultraimport('__dir__/im possible-dir ectory/my lib.python3')
```

