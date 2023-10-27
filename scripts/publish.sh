#!/bin/bash
set -euo pipefail

# Go to project base dir
pushd "$(dirname "$0")/.." >/dev/null

# Delete old stuff
rm -rf dist/ build/ src/*.egg-info/

# Rebuild lib
python3 setup.py sdist bdist_wheel

# Install required tools
python3 -m pip install twine

# Publish
python3 -m twine upload --verbose --non-interactive $@ dist/*
