# Runs a python file that builds the cython.pyx files into compiled code, then cleans the residue files

python3 build.py build_ext --inplace
rm hand.c
rm -r build