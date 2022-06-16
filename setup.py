import setuptools
import os

from itertools import chain

# Read description
with open("README.md", "r") as f:
    long_description = f.read()


with open("pyauth0/VERSION", "r") as f:
    version = f.read().strip()


# reads file lines, skips comments
def read_requirements(file):
    with open(file, "r") as f2:
        lines = [line.strip() for line in f2.readlines()]
    return [line for line in lines if line and not line.startswith("#")]


install_requires = read_requirements("requirements.txt")

# Creates the setup config for the package
# We only look for code into the "Modules" folder
setuptools.setup(
    name="pyauth0",
    version=version,
    author="Samuel Vaponi",
    author_email="samuel.vaponi.developer@gmail.com",
    description="Auth0 integration library for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/svaponi/pyauth0",
    install_requires=install_requires,
    packages=setuptools.find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # TODO SELECT A LICENSE
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
)

# Command to generate the distributions and the whl
# python3 setup.py sdist bdist_wheel
