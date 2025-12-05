#!/bin/bash
set -e

echo "--- Pulling changes for the root repository ---"
git pull

echo "\n--- Pulling changes for all submodules ---"
git submodule foreach --recursive 'git pull'

echo "\n--- Update complete ---"
