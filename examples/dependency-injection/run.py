import ultraimport

def log(msg):
    print('injected logger:', msg)

# We inject our log() function above into the worker module as logx()
worker = ultraimport('__dir__/worker.py', package='somepackage', inject={ 'logx': log })

