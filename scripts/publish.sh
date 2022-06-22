#!/bin/bash
set -euo pipefail

# Go to project base dir
pushd "$(dirname "$0")/.." >/dev/null

# rebuild lib
rm -rf dist/ build/
python setup.py bdist_wheel

# publish
python -m twine upload --verbose dist/* && {
  git tag "$(cat pyauth0/VERSION)"
  git push origin --tags
}
