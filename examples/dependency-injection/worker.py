
# Note: logx() method will be injected
if not 'logx' in globals():
    from logger import log as logx

logx('worker.py is doing some work')
