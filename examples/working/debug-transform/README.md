# Example: debug-transform

This example shows how to automatically optimize debug logging. Usually you'll log differerent messages with different priorities. The issue is that all arguments to log messages are still calculated, no matter if the log message appears or not.

You can manually wrap all your log message with something like

```python
if __debug__: log.debug(...)
```

or

```python
if DEBUG: log.debug(...)
```

Though, this is quite ugly. Why can Python not optimize those debug logs away?

I often find myself using regular expressions and commenting all debug.log() calls for a release. Afterwards you need to uncomment all of them again if you continue with the development.

Now you can use `ultraimport` and its preprocessor capabilities to solve this more elegantly. In your code, you will simply write as usual:

```python
log.debug(msg, expensive_calculation())
```

but if debug logging is turned off, it will not execut the expensive calculation. Through preprocessing, all `log.debug(` statements are wrapped with `if DEBUG:` automatically.

# How to run this example?

Use `DEBUG=1 python ./run.py` or `python DEBUG=0 python ./run.py`.

`run.py` contains the preprocess function and also imports `debug.py`.

On the first import, a file `debug__preprocessed__.py` is generated with the result of the preprocessing. Through a special loader, this file is transparently used (and updated) when you import `debug.py` through ultraimport.