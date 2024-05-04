#!/bin/bash
set -euo pipefail

echo "Rolling out '$target' version ..."

output_message="$(poetry version "$target")"

git add .
git commit -m "${output_message}"
git tag -f "$(poetry version --short)"

echo "Successfully bumped version"

read -rp "Push changes? [y/N] "
[[ ${REPLY} =~ ^[yY] ]] && git push origin "$(git rev-parse --abbrev-ref HEAD)" --tags || echo "Abort."
