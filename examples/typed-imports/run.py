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

