@echo off
title After you

color 75
echo.
echo   Initializing, please stand by...
echo.

cd /d %~dp0
git pull
for /F "tokens=* USEBACKQ" %%A in (`python -m poetry env info --path`) do call %%A\Scripts\activate.bat

streamlit run webui.py
pause