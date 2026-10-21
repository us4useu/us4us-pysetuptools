#!/usr/bin/env bash
# Builds the sdist (.tar.gz) and wheel (.whl) into dist/.
# Usage: ./build.sh  (requires: pip install build twine)
set -euo pipefail

cd "$(dirname "$0")"
rm -rf dist build ./*.egg-info
python -m build
python -m twine check dist/*
ls -1 dist
