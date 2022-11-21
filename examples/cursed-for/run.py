import ultraimport

transform = ultraimport('__dir__/v3.py', 'transform_cursed_for')

test_v3 = ultraimport('__dir__/test_v3.py', preprocessor=lambda src, file_path: transform(src.decode()))

test_v3.main()
