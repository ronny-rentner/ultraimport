# ultraimport: Dependency Injection Example

## How To Run?

```shell
 python ./run.py
injected logger: worker.py is doing some work
```

In our run.py we import worker.py and while doing that inject our own `log()` method as `logx()` into worker.py:
```python
import ultraimport

def log(msg):
    print('injected logger:', msg)

ultraimport('__dir__/worker.py', package='somepackage', inject={ 'logx': log })
```

logger.py (actually not used):
```python
def log(msg):
    print('log:', msg)

print('logger.py was imported')
```

worker.py:
```python
# Note: logx() method will be injected
if not 'logx' in globals():
    from logger import log as logx

logx('worker.py is doing some work')
```
