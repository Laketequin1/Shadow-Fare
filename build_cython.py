import os
import shutil
from distutils.core import setup
from Cython.Build import cythonize

# Change directory to build_src
os.chdir("build_src")

# Get the input from the user
input_file = input("Enter the name of the Cython file: ").strip()
input_file_path = os.path.join("src", input_file)
input_file_name = input_file.split(".")[0]

# Configure setup using cythonize
setup(
    ext_modules=cythonize(input_file_path, language_level=3),
    script_args=["build_ext", "--inplace"]
)

# Delete temp files
os.remove(os.path.join("src", f"{input_file_name}.c"))
shutil.rmtree("build")

# Get the current directory
current_directory = os.getcwd()

# Iterate over the files in the directory
for filename in os.listdir(current_directory):
    if filename.startswith(input_file_name) and (filename.endswith(".so") or filename.endswith(".pyd")):
        # Get the extension of the file
        extension = os.path.splitext(filename)[1]
        # Create the new filename
        new_filename = f"{input_file_name}{extension}"
        # Rename the file
        os.rename(filename, new_filename)
        break

# Change back to the previous directory
os.chdir("..")

# Move the created .pyd file to the "src" folder
extension = ".pyd" if os.name == "nt" else ".so"
created_file = f"{input_file_name}{extension}"
shutil.move(os.path.join("build_src", created_file), os.path.join("src", created_file))
