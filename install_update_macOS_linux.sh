#!/bin/bash

echo "Changing to script directory"
cd "$(dirname "$0")"

echo "-git: updating repository"
git pull

echo "-updating dependencies"
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple poetry
python -m poetry config virtualenvs.in-project true
python -m poetry install

source $(python -m poetry env info --path)/bin/activate
pre-commit install

python "$(pwd)/afteryou/update_routine.py"
read -p "Press any key to continue ..."
python "$(pwd)/afteryou/install_setting.py"
read -p "Press any key to continue ..."
