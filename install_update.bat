@echo off
title installing dependence and updating

cd /d %~dp0

@REM echo -git: updating repository
@REM git pull

echo -updating dependencies
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple poetry
python -m poetry config virtualenvs.in-project true
python -m poetry install

for /F "usebackq tokens=*" %%A in (`python -m poetry env info --path`) do call %%A\Scripts\activate.bat
pre-commit install

python "%~dp0\afteryou\update_routine.py"
pause