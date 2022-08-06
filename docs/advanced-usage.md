# ultraimport: Advanced Usage

Check the [ultraimport Github Page](https://github.com/ronny-rentner/ultraimport) for an overview.

## Import impossible filename and directory

With ultraimport, you can import from any file or directory, even if it contains spaces or dashes or if the file name contains any other file extension.

See [examples/working/impossible-filename](/examples/working/impossible-filename)

run.py:
```python
import ultraimport

ultraimport('__dir__/im possible-dir ectory/my lib.python3')
```

## Typed imports

Get type safty by specifying what type you expect a certain imported object to be.

See [examples/working/typed-imports](/examples/working/typed-imports)

run.py:
```python
import ultraimport, typing

myfunction, mystring = ultraimport('__dir__/mylib.py', { 'myfunction': typing.Callable, 'mystring': str })

print(myfunction, type(myfunction))
print(mystring, type(mystring))

try:
    myint = ultraimport('__dir__/mylib.py', { 'myint': str })

    # If we reach this point, the exception wasn't thrown
    print('No type mismatch detected')

    print(myint, type(myint))

except TypeError as e:
    print('Type mismatch detected')
    print(e)
```

