#!/bin/bash
set -eu

if ! remote="$(git remote get-url origin)"; then
    echo "Configure origin with the confirmed GitHub repository URL before building for deployment." >&2
    exit 1
fi

remote="${remote%/}"
repo_name="${remote##*/}"
repo_name="${repo_name%.git}"
python3 src/main.py "/${repo_name}/"
