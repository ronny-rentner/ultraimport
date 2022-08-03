# ultraimport: Preprocessing Example

This example shows how to use a preprocessor to change Python source code on the fly. We will automatically optimize debug logging. Usually you'll log differerent messages with different priorities. The issue is that all arguments to log messages are still calculated, no matter if the log message actually appears or not.

You can manually wrap all your log message with something like

```python
if __debug__: log.debug(...)
```

or

```python
if DEBUG: log.debug(...)
```

Though, this is quite ugly in the source code. I often find myself using regular expressions and commenting all debug.log() calls for a release. Afterwards you need to uncomment all of them again if you continue with the development.  Now you can use `ultraimport` and its preprocessor capabilities to solve this more elegantly. In your code, you will simply write as usual:

```python
log.debug(msg, expensive_calculation())
```

but if debug logging is turned off, it will not execut the expensive calculation. Through preprocessing, all `log.debug()` statements are wrapped with `if DEBUG:` automatically.

# How to run this example?

Use `DEBUG=0 python ./run.py` and you not should see a message like _'Simulating expensive calculation: sleeping 1 second now'_.

`run.py` contains the preprocess function and also imports `debug.py`.

On the first import, a file `debug__preprocessed__.py` is generated with the result of the preprocessing. Through a special loader, this file is transparently used (and updated) when you import `debug.py` through ultraimport.

```shell
$ DEBUG=0 python ./run.py
Preprocessing..
DEBUG: False
Production timings with no debug prints:
first() 0.05868230201303959
second() 0.05797609454020858
third() 0.12420633807778358
```

As you can see, the `third()` function is still slower then the preprocessing approach from the `first()` function, even though it avoids executing the expensive calculation.
