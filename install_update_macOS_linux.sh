#!/bin/sh

cd "$(dirname "$0")"

echo "-git: updating repository"
git pull

echo "-updating dependencies"
pip3 install poetry --user
python3 -m poetry config virtualenvs.in-project true
python3 -m poetry install

source $(python3 -m poetry env info --path)/bin/activate
pip3 install pre-commit

python3 -m afteryou.update_routine
read -n 1 -s -r -p "Press any key to continue..."
python3 -m afteryou.install_setting
read -n 1 -s -r -p "Press any key to continue..."