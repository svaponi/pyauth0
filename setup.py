import setuptools

with open("README.md", "r") as f:
    long_description = f.read()


with open("pyauth0/VERSION", "r") as f:
    version = f.read().strip()


# reads file lines, skips comments
def read_requirements(file):
    with open(file, "r") as f2:
        lines = [line.strip() for line in f2.readlines()]
    return [line for line in lines if line and not line.startswith("#")]


requirements = read_requirements("requirements.txt")
test_requirements = read_requirements("test/requirements.txt")

# Creates the setup config for the package
# We only look for code into the "Modules" folder
setuptools.setup(
    name="pyauth0",
    version=version,
    author="svaponi",
    author_email="svaponi@proton.me",
    description="Python utilities for Auth0",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/svaponi/pyauth0",
    install_requires=requirements,
    extras_require={
        "test": test_requirements,
    },
    packages=setuptools.find_packages(exclude=["*.test", "*.test.*", "test.*", "test"]),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

# Command to generate the distributions and the whl
# python3 setup.py sdist bdist_wheel
