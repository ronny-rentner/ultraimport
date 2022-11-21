from pathlib import Path
from setuptools import setup, Extension
import Cython.Build

ext = Extension(name="ultraimport", sources=["ultraimport.py"])

setup(
    name='ultraimport',
    cmdclass={'build_ext': Cython.Build.build_ext},
    package_dir={'ultraimport': '.'},
    packages=['ultraimport'],
    zip_safe=False,
    ext_modules=Cython.Build.cythonize(ext, compiler_directives={'language_level' : "3"}),
    setup_requires=['cython>=0.24.1'],
)
