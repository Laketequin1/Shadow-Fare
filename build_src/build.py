# Builds the cython.pyx files into compiled code

from distutils.core import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("hand.pyx")
)
