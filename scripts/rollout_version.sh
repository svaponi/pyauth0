#!/bin/bash
set -euo pipefail

function fail() {
  echo >&2 -e "\033[31m$@\033[m"
  exit 1
}

target="${1:-patch}"
echo "Rolling out '$target' version ..."
[[ "$target" =~ patch|minor|major ]] || fail "Invalid target: '$target'. Allowed values are: 'patch|minor|major' (default is 'patch')"

version_file="$(find src -name VERSION | head -n1)"
old_version="$(cat "$version_file")"

major="$(echo "$old_version" | cut -d'.' -f1)"
minor="$(echo "$old_version" | cut -d'.' -f2)"
patch="$(echo "$old_version" | cut -d'.' -f3)"
if [ "$target" == "major" ]; then
  minor=0
  patch=0
elif [ "$target" == "minor" ]; then
  patch=0
fi

let "$target=$target+1"
new_version="${major}.${minor}.${patch}"

echo "${new_version}" > "$version_file"

git add .
git commit -m "bump version to ${new_version} (from ${old_version})"
git tag -f "${new_version}"

echo "Successfully bumped version to ${new_version} (from ${old_version})"
read -rp "Push changes? [y/N] "
[[ ${REPLY} =~ ^[yY] ]] && git push origin "$(git rev-parse --abbrev-ref HEAD)" --tags || echo "Abort."