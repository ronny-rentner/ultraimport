import ultraimport

def log(msg):
    print('injected logger:', msg)

ultraimport('__dir__/worker.py', package='somepackage', inject={ 'logx': log })

