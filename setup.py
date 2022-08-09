from pathlib import Path
from setuptools import setup, Extension
import Cython.Build

this_directory = Path(__file__).parent
long_description = (this_directory / "readme.md").read_text(encoding='UTF-8')

version = '0.0.6'

ext = Extension(name="ultraimport", sources=["ultraimport.py"])

setup(
    name='ultraimport',
    version=version,
    description='Reliable, file system based imports -- no matter how you run your code',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Ronny Rentner',
    author_email='ultraimport.code@ronny-rentner.de',
    url='https://github.com/ronny-rentner/ultraimport',
    cmdclass={'build_ext': Cython.Build.build_ext},
    package_dir={'ultraimport': '.'},
    packages=['ultraimport'],
    zip_safe=False,
    ext_modules=Cython.Build.cythonize(ext, compiler_directives={'language_level' : "3"}),
    setup_requires=['cython>=0.24.1'],
    python_requires=">=3.5",
)
