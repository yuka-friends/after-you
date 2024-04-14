@echo off
title installing dependence and updating

cd /d %~dp0

echo -git: updating repository
git pull

echo -updating dependencies
python -m pip install -i https://pypi.tuna.tsinghua.edu.cn/simple poetry
python -m poetry config virtualenvs.in-project true
python -m poetry install
@REM python -m poetry update

for /F "usebackq tokens=*" %%A in (`python -m poetry env info --path`) do call %%A\Scripts\activate.bat
pre-commit install

python -m textblob.download_corpora

python "%~dp0\afteryou\update_routine.py"
echo.
pause
python "%~dp0\afteryou\install_setting.py"
pause